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


def convert_to_pdf(notebook_path: Path) -> Path:
    """Convert a Jupyter notebook to PDF using nbconvert + playwright."""
    pdf_filename = f"{notebook_path.stem}.pdf"
    pdf_path = TEMP_DIR / pdf_filename

    # Ensure playwright browsers are installed
    subprocess.run(["playwright", "install", "chromium"], check=False)

    cmd = [
        "jupyter", "nbconvert", "--to", "webpdf",
        "--output-dir", str(TEMP_DIR),
        "--output", pdf_filename,
        str(notebook_path)
    ]
    print(f"Converting: {notebook_path.name} to PDF...")
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

    # Convert notebooks to PDF
    pdfs = {}
    if NOTEBOOK_EN.exists():
        print(f"\nEN notebook found: {NOTEBOOK_EN.name}")
        pdfs['en'] = convert_to_pdf(NOTEBOOK_EN)
    else:
        print(f"\nWARNING: EN notebook not found at {NOTEBOOK_EN}")

    if NOTEBOOK_ES.exists():
        print(f"\nES notebook found: {NOTEBOOK_ES.name}")
        pdfs['es'] = convert_to_pdf(NOTEBOOK_ES)
    else:
        print(f"\nWARNING: ES notebook not found at {NOTEBOOK_ES}")

    if not pdfs:
        print("ERROR: No notebooks found to process.")
        sys.exit(1)

    # Upload to Google Drive
    service = get_authenticated_service()

    # Create folder structure: first_round/
    print(f"\nCreating/verifying folder structure in Drive...")
    first_round_id = create_or_get_folder(service, "first_round", ROOT_FOLDER_ID)

    # Create technical_backup/ and executive_reports/
    tech_backup_id = create_or_get_folder(service, "technical_backup", first_round_id)
    exec_reports_id = create_or_get_folder(service, "executive_reports", first_round_id)

    # Process each language
    for lang, notebook_path in [('en', NOTEBOOK_EN), ('es', NOTEBOOK_ES)]:
        if not notebook_path.exists():
            continue

        print(f"\n{'=' * 40}")
        print(f"Processing language: {lang.upper()}")
        print(f"{'=' * 40}")

        # 1. TECHNICAL BACKUP (notebook + PDF)
        print("\n📁 Uploading to technical_backup/...")
        lang_folder_id = create_or_get_folder(service, lang.upper(), tech_backup_id)

        print("   Uploading notebook...")
        upload_file(service, notebook_path, lang_folder_id, 'application/x-ipynb+json')

        print("   Uploading PDF...")
        pdf_path = pdfs[lang]
        upload_file(service, pdf_path, lang_folder_id, 'application/pdf')

        # 2. EXECUTIVE REPORTS (only PDF, cleaner format)
        # Note: For executive reports, you would use a cleaned version of the PDF
        # For now, it uploads the same PDF (you can replace with cleaned version later)
        print("\n📁 Uploading to executive_reports/...")
        exec_lang_folder_id = create_or_get_folder(service, lang.upper(), exec_reports_id)

        # Rename for executive report
        exec_pdf_name = f"electoral_report_2025_{lang.upper()}.pdf"
        exec_pdf_path = TEMP_DIR / exec_pdf_name

        # Copy/symlink the same PDF with new name
        if pdf_path.exists():
            import shutil
            shutil.copy(pdf_path, exec_pdf_path)
            upload_file(service, exec_pdf_path, exec_lang_folder_id, 'application/pdf')
            exec_pdf_path.unlink()  # clean up

    # Clean up temporary files
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
    print(f"       │   ├── EN/ (notebook.ipynb + .pdf)")
    print(f"       │   └── ES/ (notebook.ipynb + .pdf)")
    print(f"       └── executive_reports/")
    print(f"           ├── EN/ (electoral_report_2025_EN.pdf)")
    print(f"           └── ES/ (electoral_report_2025_ES.pdf)")
    print("=" * 60)


if __name__ == "__main__":
    main()
