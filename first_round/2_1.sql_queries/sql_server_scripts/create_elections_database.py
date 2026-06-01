#!/usr/bin/env python3

"""
Database Builder for Chilean Election Results 2025 - SQL Server
===============================================================
Automated script to download election results CSV from GitHub and create
a SQL Server database with structured tables ready for analysis.

Features:
- Downloads CSV from raw GitHub URL
- Auto-detects column data types (INT, DECIMAL, NVARCHAR)
- Generates CREATE TABLE and INSERT statements
- Creates SQL script file for manual execution
- Optional direct execution via pyodbc
- Handles batch inserts (500 rows per batch)

Output:
- create_database.sql : Complete SQL script with CREATE TABLE + INSERTs
- Optional: Direct SQL Server connection execution

Directory Structure:
sql_server_scripts/
├── create_database.sql          # Generated SQL script
├── temp_data.csv                 # Temporary downloaded CSV (cleaned up)
└── create_elections_database.py # This script

Requirements:
- Python 3.7+
- pandas
- pyodbc (optional, for direct execution)
- ODBC Driver 17 for SQL Server

Author: Alfonso Droguett
License: MIT
"""

import pandas as pd
import urllib.request
import argparse
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# ============================================================================
# DIRECTORY STRUCTURE (following established pattern)
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "sql_server_scripts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_CSV = OUTPUT_DIR / "temp_data.csv"
SQL_OUTPUT = OUTPUT_DIR / "create_database.sql"

# ============================================================================
# CONFIGURATION
# ============================================================================
# Raw CSV URL from GitHub
CSV_URL = "https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/raw/chile_2025_first_round.csv"

# SQL Server connection settings (adjust for your environment)
# Option 1: Windows Authentication
CONNECTION_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=EleccionesChile2025;"
    "Trusted_Connection=yes;"
)

# Option 2: SQL Server Authentication (uncomment and modify)
# CONNECTION_STRING = (
#     "Driver={ODBC Driver 17 for SQL Server};"
#     "Server=localhost;"
#     "Database=EleccionesChile2025;"
#     "UID=your_username;"
#     "PWD=your_password;"
# )

# Batch size for INSERT statements
BATCH_SIZE = 500

# Table name for the election data
TABLE_NAME = "first_round_2025"

# Database name
DATABASE_NAME = "EleccionesChile2025"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def cleanup_temp_files():
    """Remove temporary CSV file after processing."""
    if TEMP_CSV.exists():
        try:
            TEMP_CSV.unlink()
            print(f"   🧹 Cleaned up: {TEMP_CSV}")
        except Exception as e:
            print(f"   ⚠️ Could not delete temp file: {e}")


def get_python_type_to_sql(dtype) -> str:
    """
    Map pandas dtype to SQL Server data type.

    Args:
        dtype: pandas dtype (int64, float64, object, etc.)

    Returns:
        str: SQL Server data type
    """
    if dtype == 'int64':
        return 'INT'
    elif dtype == 'float64':
        return 'DECIMAL(10,2)'
    else:
        return 'NVARCHAR(100)'


# ============================================================================
# DATA DOWNLOAD AND PROCESSING
# ============================================================================
def download_csv(url: str) -> pd.DataFrame:
    """
    Download CSV from GitHub URL and load into DataFrame.

    Args:
        url: Raw GitHub URL for the CSV file

    Returns:
        pd.DataFrame: Loaded election data
    """
    print(f"📥 Downloading data from: {url}")
    
    try:
        urllib.request.urlretrieve(url, TEMP_CSV)
        df = pd.read_csv(TEMP_CSV, encoding='utf-8-sig')
        print(f"✅ Downloaded: {len(df):,} rows, {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        return df
    except Exception as e:
        print(f"❌ Error downloading CSV: {e}")
        raise


def analyze_dataframe(df: pd.DataFrame) -> None:
    """
    Print summary statistics of the DataFrame.

    Args:
        df: pandas DataFrame with election data
    """
    print("\n📊 Data Summary:")
    print(f"   Total communes: {len(df):,}")
    print(f"   Total columns: {len(df.columns)}")
    
    # Count candidate columns (those ending with _votes or _pct)
    candidate_vote_cols = [c for c in df.columns if c.endswith('_votes') and c not in ['blank_votes', 'null_votes', 'casted_votes']]
    candidate_pct_cols = [c for c in df.columns if c.endswith('_pct') and c not in ['blank_pct', 'null_pct', 'casted_pct']]
    
    print(f"   Candidates: {len(candidate_vote_cols)}")
    print(f"   Sample commune: {df['commune'].iloc[0]}")
    print(f"   Sample region: {df['region'].iloc[0]}")


# ============================================================================
# SQL GENERATION FUNCTIONS
# ============================================================================
def generate_create_table_sql(df: pd.DataFrame, table_name: str) -> str:
    """
    Generate CREATE TABLE statement based on DataFrame columns.

    Args:
        df: pandas DataFrame with election data
        table_name: Name of the SQL table to create

    Returns:
        str: CREATE TABLE SQL statement
    """
    columns = []
    for col in df.columns:
        sql_type = get_python_type_to_sql(str(df[col].dtype))
        columns.append(f"    [{col}] {sql_type}")
    
    sql = f"""
-- =====================================================
-- CREATE TABLE {table_name}
-- =====================================================
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Source: {CSV_URL}
-- Rows: {len(df):,}
-- Columns: {len(df.columns)}
-- =====================================================

USE {DATABASE_NAME};
GO

IF OBJECT_ID('{table_name}', 'U') IS NOT NULL
    DROP TABLE {table_name};
GO

CREATE TABLE {table_name} (
{',\n'.join(columns)}
);
GO
"""
    return sql


def generate_insert_sql(df: pd.DataFrame, table_name: str, batch_size: int = 500) -> str:
    """
    Generate INSERT statements in batches for SQL Server.

    Args:
        df: pandas DataFrame with election data
        table_name: Name of the SQL table
        batch_size: Number of rows per INSERT batch

    Returns:
        str: INSERT SQL statements with GO separators
    """
    inserts = []
    rows = df.values.tolist()
    columns_list = ', '.join([f'[{col}]' for col in df.columns])
    
    print(f"   📝 Generating INSERT statements ({len(rows):,} rows, batch size: {batch_size})...")
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        values_batch = []
        
        for row in batch:
            values = []
            for val in row:
                if pd.isna(val):
                    values.append('NULL')
                elif isinstance(val, str):
                    # Escape single quotes by doubling them
                    escaped = str(val).replace("'", "''")
                    values.append(f"'{escaped}'")
                else:
                    values.append(str(val))
            values_batch.append(f"({', '.join(values)})")
        
        insert_block = f"""
-- Batch {i//batch_size + 1}: Rows {i+1} to {min(i+batch_size, len(rows))}
INSERT INTO {table_name} ({columns_list})
VALUES {',\n'.join(values_batch)};
GO
"""
        inserts.append(insert_block)
    
    return '\n'.join(inserts)


def generate_complete_sql_script(df: pd.DataFrame, table_name: str) -> str:
    """
    Generate complete SQL script with both CREATE TABLE and INSERT statements.

    Args:
        df: pandas DataFrame with election data
        table_name: Name of the SQL table

    Returns:
        str: Complete SQL script
    """
    print("\n🔧 Generating SQL script...")
    
    header = f"""-- =====================================================
-- DATABASE SCRIPT - CHILEAN ELECTIONS 2025
-- =====================================================
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Source: {CSV_URL}
-- Table: {table_name}
-- Total rows: {len(df):,}
-- Total columns: {len(df.columns)}
-- =====================================================

"""
    
    create_sql = generate_create_table_sql(df, table_name)
    insert_sql = generate_insert_sql(df, table_name, BATCH_SIZE)
    
    return header + create_sql + insert_sql


def save_sql_script(sql_content: str, output_path: Path) -> None:
    """
    Save SQL script to file.

    Args:
        sql_content: Complete SQL script content
        output_path: Path to save the SQL file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print(f"✅ SQL script saved to: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"❌ Error saving SQL script: {e}")
        raise


# ============================================================================
# SQL SERVER EXECUTION FUNCTIONS
# ============================================================================
def test_sql_server_connection(conn_str: str) -> bool:
    """
    Test connection to SQL Server.

    Args:
        conn_str: ODBC connection string

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        import pyodbc
        test_conn = pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Trusted_Connection=yes;"
        )
        test_conn.close()
        print("✅ SQL Server connection successful")
        return True
    except ImportError:
        print("⚠️ pyodbc not installed")
        return False
    except Exception as e:
        print(f"⚠️ Cannot connect to SQL Server: {e}")
        return False


def create_database_if_not_exists(conn_str: str, db_name: str) -> bool:
    """
    Create database if it doesn't exist.

    Args:
        conn_str: ODBC connection string
        db_name: Name of the database to create

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import pyodbc
        # Connect to master to create database
        master_conn = pyodbc.connect(
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server=localhost;"
            f"Trusted_Connection=yes;"
        )
        cursor = master_conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{db_name}'")
        exists = cursor.fetchone()[0]
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created")
        else:
            print(f"ℹ️ Database '{db_name}' already exists")
        
        master_conn.commit()
        cursor.close()
        master_conn.close()
        return True
        
    except ImportError:
        return False
    except Exception as e:
        print(f"⚠️ Error creating database: {e}")
        return False


def execute_sql_direct(conn_str: str, sql_script: str) -> bool:
    """
    Execute SQL script directly on SQL Server.

    Args:
        conn_str: ODBC connection string
        sql_script: Complete SQL script to execute

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import pyodbc
        
        # Split by GO statements
        statements = sql_script.split('GO')
        
        # Connect to the specific database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        total_statements = 0
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    if cursor.description:
                        cursor.fetchall()
                    total_statements += 1
                except Exception as e:
                    print(f"⚠️ Error in statement: {e[:100]}...")
                    # Continue with next statement
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Executed {total_statements} SQL statements")
        return True
        
    except ImportError:
        print("⚠️ pyodbc not installed. Cannot execute directly.")
        return False
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        return False


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Create SQL Server database from Chilean election results CSV'
    )
    parser.add_argument(
        '--no-execute', action='store_true',
        help='Generate SQL script only, do not execute directly'
    )
    parser.add_argument(
        '--batch-size', type=int, default=500,
        help='Number of rows per INSERT batch (default: 500)'
    )
    parser.add_argument(
        '--table', type=str, default=TABLE_NAME,
        help=f'Table name (default: {TABLE_NAME})'
    )
    
    args = parser.parse_args()
    
    # Override batch size if provided
    global BATCH_SIZE
    BATCH_SIZE = args.batch_size
    
    print("\n" + "=" * 70)
    print("🗄️  SQL SERVER DATABASE BUILDER - CHILEAN ELECTIONS 2025")
    print("=" * 70)
    print(f"📥 Source: {CSV_URL}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"📊 Table name: {args.table}")
    print(f"📦 Batch size: {BATCH_SIZE} rows")
    print("=" * 70)
    
    try:
        # Step 1: Download and load data
        print("\n1️⃣ DOWNLOADING DATA...")
        df = download_csv(CSV_URL)
        
        # Step 2: Analyze data
        analyze_dataframe(df)
        
        # Step 3: Generate SQL script
        print("\n2️⃣ GENERATING SQL SCRIPT...")
        sql_script = generate_complete_sql_script(df, args.table)
        
        # Step 4: Save SQL script
        save_sql_script(sql_script, SQL_OUTPUT)
        
        # Step 5: Optionally execute directly
        print("\n3️⃣ SQL SERVER CONNECTION...")
        
        if args.no_execute:
            print("ℹ️ Direct execution disabled (--no-execute flag)")
            print("📁 Use the generated SQL script manually:")
            print(f"   {SQL_OUTPUT}")
        else:
            # Check if pyodbc is available
            try:
                import pyodbc
                print("✅ pyodbc found")
                
                # Test connection
                if test_sql_server_connection(CONNECTION_STRING):
                    # Create database if needed
                    create_database_if_not_exists(CONNECTION_STRING, DATABASE_NAME)
                    
                    # Execute SQL directly
                    print("\n4️⃣ EXECUTING SQL SCRIPT...")
                    if execute_sql_direct(CONNECTION_STRING, sql_script):
                        print(f"✅ Table '{args.table}' created and populated with {len(df):,} rows")
                    else:
                        print("⚠️ Direct execution failed. Use generated SQL script.")
                else:
                    print("⚠️ Could not connect to SQL Server")
                    print("📁 Use the generated SQL script manually")
                    
            except ImportError:
                print("⚠️ pyodbc not installed")
                print("   Install with: pip install pyodbc")
                print("📁 Use the generated SQL script manually")
        
        # Step 6: Cleanup
        print("\n5️⃣ CLEANING UP...")
        cleanup_temp_files()
        
        # Final summary
        print("\n" + "=" * 70)
        print("✅ PROCESS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"📁 Generated files:")
        print(f"   • {SQL_OUTPUT}")
        print(f"\n📝 Next steps:")
        print(f"   1. Open {SQL_OUTPUT} in SQL Server Management Studio")
        print(f"   2. Execute the script to create the database and table")
        print(f"   3. Or run with --no-execute flag to skip direct execution")
        print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Execution interrupted by user")
        cleanup_temp_files()
        return 1
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        cleanup_temp_files()
        return 1


if __name__ == "__main__":
    sys.exit(main())
