#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notebook to PDF Exporter + Google Drive Uploader - Electoral Analysis
====================================================================
Exports electoral analysis notebooks (EN and ES) to PDF and uploads them to Google Drive.

Structure in Drive:
   Chilean Elections 2025 Analysis/
   └── first_round/
       ├── technical_backup/
       │   ├── EN/
       │   │   ├── electoral_analysis_2025_EN.ipynb
       │   │   └── electoral_analysis_2025_EN.pdf
       │   └── ES/
       │       ├── electoral_analysis_2025_ES.ipynb
       │       └── electoral_analysis_2025_ES.pdf
       └── executive_reports/
           ├── EN/
           │   └── electoral_report_2025_EN.pdf
           └── ES/
               └── electoral_report_2025_ES.pdf

Requirements:
- Python 3.7+
- jupyter, nbconvert, playwright
- google-api-python-client, google-auth-oauthlib

Environment Variables:
    GDRIVE_CLIENT_ID
    GDRIVE_CLIENT_SECRET
    GDRIVE_REFRESH_TOKEN
    GDRIVE_ROOT_FOLDER_ID

Author: Alfonso Droguett
License: MIT
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ============================================================================
# PATH CONFIGURATION
# ============================================================================
# Notebooks source
NOTEBOOK_EN = Path("first_round/2_2.notebooks/electoral_analysis_2025_EN.ipynb")
NOTEBOOK_ES = Path("first_round/2_2.notebooks/electoral_analysis_2025_ES.ipynb")

# Temporary directory for PDFs
TEMP_DIR = Path("temp_pdf")
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================================
# ENVIRONMENT VARIABLES (required)
# ============================================================================
CLIENT_ID = os.environ.get("GDRIVE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GDRIVE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("GDRIVE_REFRESH_TOKEN")
ROOT_FOLDER_ID = os.environ.get("GDRIVE_ROOT_FOLDER_ID")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ROOT_FOLDER_ID]):
    print("ERROR: Missing required environment variables.")
    print("Required: GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN, GDRIVE_ROOT_FOLDER_ID")
    sys.exit(1)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_authenticated_service():
    """Build and return an authenticated Google Drive service."""
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    if creds.expired:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)


def convert_to_pdf(notebook_path: Path, hide_code: bool = True) -> Path:
    """
    Convert a Jupyter notebook to PDF using nbconvert + playwright.
    
    Args:
        notebook_path: Path to the .ipynb file
        hide_code: If True, removes code cells from output (--no-input)
    
    Returns:
        Path: Path to the generated PDF file
    """
    pdf_filename = f"{notebook_path.stem}.pdf"
    pdf_path = TEMP_DIR / pdf_filename

    # Ensure playwright browsers are installed
    subprocess.run(["playwright", "install", "chromium"], check=False)

    # Build command
    cmd = [
        "jupyter", "nbconvert", "--to", "webpdf",
        "--output-dir", str(TEMP_DIR),
        "--output", pdf_filename,
        str(notebook_path)
    ]
    
    # Add --no-input to hide code cells (for executive reports)
    if hide_code:
        cmd.insert(3, "--no-input")
        print(f"Converting (hide_code=True): {notebook_path.name} to PDF...")
    else:
        print(f"Converting (hide_code=False): {notebook_path.name} to PDF...")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("nbconvert error:")
        print(result.stderr)
        sys.exit(1)

    if not pdf_path.exists():
        print(f"PDF not found at expected path: {pdf_path}")
        sys.exit(1)

    print(f"PDF generated: {pdf_path}")
    return pdf_path


def create_or_get_folder(service, folder_name: str, parent_id: str) -> str:
    """Create a folder in Google Drive if it doesn't exist, otherwise return its ID."""
    query = (f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' "
             f"and '{parent_id}' in parents and trashed=false")
    response = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = response.get('files', [])

    if files:
        print(f"   Folder exists: {folder_name}")
        return files[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        print(f"   Folder created: {folder_name}")
        return folder['id']


def upload_file(service, file_path: Path, parent_folder_id: str, mime_type: str) -> str:
    """Upload a file to Google Drive."""
    media = MediaFileUpload(file_path, mimetype=mime_type)
    metadata = {'name': file_path.name, 'parents': [parent_folder_id]}
    uploaded = service.files().create(body=metadata, media_body=media, fields='id').execute()
    print(f"   Uploaded: {file_path.name}")
    return uploaded['id']


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "=" * 60)
    print("ELECTORAL ANALYSIS NOTEBOOKS → PDF + GOOGLE DRIVE")
    print("=" * 60)

    # Validate source notebooks
    if not NOTEBOOK_EN.exists() and not NOTEBOOK_ES.exists():
        print("ERROR: Neither EN nor ES notebook found.")
        print(f"Expected: {NOTEBOOK_EN}")
        print(f"Expected: {NOTEBOOK_ES}")
        sys.exit(1)

    # =========================================
    # 1. Convert to PDF for TECHNICAL BACKUP (with code)
    # =========================================
    print("\n" + "-" * 40)
    print("STEP 1: Converting for TECHNICAL BACKUP (with code)")
    print("-" * 40)
    
    pdfs_tech = {}
    if NOTEBOOK_EN.exists():
        print(f"\nEN notebook found: {NOTEBOOK_EN.name}")
        pdfs_tech['en'] = convert_to_pdf(NOTEBOOK_EN, hide_code=False)
    else:
        print(f"\nWARNING: EN notebook not found at {NOTEBOOK_EN}")

    if NOTEBOOK_ES.exists():
        print(f"\nES notebook found: {NOTEBOOK_ES.name}")
        pdfs_tech['es'] = convert_to_pdf(NOTEBOOK_ES, hide_code=False)
    else:
        print(f"\nWARNING: ES notebook not found at {NOTEBOOK_ES}")

    # =========================================
    # 2. Convert to PDF for EXECUTIVE REPORTS (without code)
    # =========================================
    print("\n" + "-" * 40)
    print("STEP 2: Converting for EXECUTIVE REPORTS (without code)")
    print("-" * 40)
    
    pdfs_exec = {}
    if NOTEBOOK_EN.exists():
        print(f"\nEN notebook found: {NOTEBOOK_EN.name}")
        pdfs_exec['en'] = convert_to_pdf(NOTEBOOK_EN, hide_code=True)
    else:
        print(f"\nWARNING: EN notebook not found at {NOTEBOOK_EN}")

    if NOTEBOOK_ES.exists():
        print(f"\nES notebook found: {NOTEBOOK_ES.name}")
        pdfs_exec['es'] = convert_to_pdf(NOTEBOOK_ES, hide_code=True)
    else:
        print(f"\nWARNING: ES notebook not found at {NOTEBOOK_ES}")

    if not pdfs_tech and not pdfs_exec:
        print("ERROR: No notebooks found to process.")
        sys.exit(1)

    # =========================================
    # 3. Upload to Google Drive
    # =========================================
    print("\n" + "-" * 40)
    print("STEP 3: Uploading to Google Drive")
    print("-" * 40)
    
    service = get_authenticated_service()

    # Create folder structure: first_round/
    print(f"\nCreating/verifying folder structure in Drive...")
    first_round_id = create_or_get_folder(service, "first_round", ROOT_FOLDER_ID)

    # Create technical_backup/ and executive_reports/
    tech_backup_id = create_or_get_folder(service, "technical_backup", first_round_id)
    exec_reports_id = create_or_get_folder(service, "executive_reports", first_round_id)

    # =========================================
    # 4. Upload TECHNICAL BACKUP (notebook + PDF with code)
    # =========================================
    print("\n" + "=" * 40)
    print("UPLOADING TECHNICAL BACKUP (with code)")
    print("=" * 40)
    
    for lang, notebook_path in [('en', NOTEBOOK_EN), ('es', NOTEBOOK_ES)]:
        if not notebook_path.exists():
            continue

        print(f"\nProcessing language: {lang.upper()}")
        print("-" * 30)
        
        lang_folder_id = create_or_get_folder(service, lang.upper(), tech_backup_id)

        print("   Uploading notebook...")
        upload_file(service, notebook_path, lang_folder_id, 'application/x-ipynb+json')

        print("   Uploading PDF (with code)...")
        pdf_path = pdfs_tech[lang]
        upload_file(service, pdf_path, lang_folder_id, 'application/pdf')

    # =========================================
    # 5. Upload EXECUTIVE REPORTS (only PDF without code)
    # =========================================
    print("\n" + "=" * 40)
    print("UPLOADING EXECUTIVE REPORTS (without code)")
    print("=" * 40)
    
    for lang, notebook_path in [('en', NOTEBOOK_EN), ('es', NOTEBOOK_ES)]:
        if not notebook_path.exists():
            continue

        print(f"\nProcessing language: {lang.upper()}")
        print("-" * 30)
        
        lang_folder_id = create_or_get_folder(service, lang.upper(), exec_reports_id)

        # Rename for executive report
        exec_pdf_name = f"electoral_report_2025_{lang.upper()}.pdf"
        exec_pdf_path = TEMP_DIR / exec_pdf_name

        # Copy the PDF (without code) with new name
        pdf_path = pdfs_exec[lang]
        if pdf_path.exists():
            shutil.copy(pdf_path, exec_pdf_path)
            upload_file(service, exec_pdf_path, lang_folder_id, 'application/pdf')
            exec_pdf_path.unlink()  # clean up

    # =========================================
    # 6. Clean up temporary files
    # =========================================
    for f in TEMP_DIR.glob("*.pdf"):
        f.unlink()
    print("\n✅ Temporary files removed.")

    print("\n" + "=" * 60)
    print("EXPORT COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nDrive structure:")
    print(f"   {ROOT_FOLDER_ID}/")
    print(f"   └── first_round/")
    print(f"       ├── technical_backup/")
    print(f"       │   ├── EN/ (notebook.ipynb + PDF with code)")
    print(f"       │   └── ES/ (notebook.ipynb + PDF with code)")
    print(f"       └── executive_reports/")
    print(f"           ├── EN/ (electoral_report_2025_EN.pdf - NO code)")
    print(f"           └── ES/ (electoral_report_2025_ES.pdf - NO code)")
    print("=" * 60)


if __name__ == "__main__":
    main()
