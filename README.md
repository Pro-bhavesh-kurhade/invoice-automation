# InvoiceDesk — Local Invoice Review Starter

A lightweight starter project for a local invoice-review web app. The interface runs in a browser, while Flask and SQLite run on the same Windows PC.

## Current features
- Upload multiple PDF/JPG/PNG/WEBP files (25 MB per file).
- Store uploaded originals in the local `uploads/` folder.
- View image/PDF files beside a manual review form.
- Record invoice type, party name, GSTIN, invoice number/date, values and a proposed Tally ledger.
- Save review status and notes.
- Keep a basic SQLite audit log of uploads and review saves.
- Bind the web server to `127.0.0.1` only (not exposed to the local network).

## Not implemented yet
- OCR extraction.
- GSTIN verification against the GST portal.
- Tally connectivity, ledger-master retrieval or voucher matching.
- Automated duplicate detection and tax validation.
- Voucher creation/posting.
- Authentication and multi-user controls.

**Do not use this starter to post accounting entries.** “Approved” currently records a manual status only. It does not verify accounting data or create a Tally voucher.

## Requirements
- Windows 10/11.
- Python 3.11 or newer installed from python.org.
- Internet for the first dependency installation (Flask only). Runtime use is local.

## Run on Windows
1. Extract this ZIP into a normal folder, for example `C:\InvoiceDesk`.
2. Double-click `start_windows.bat`.
3. On first run it creates a local `.venv` and installs Flask.
4. Your browser should open `http://127.0.0.1:5000`.
5. Keep the terminal window open while using the app. Close it to stop the app.

If the browser does not open, visit `http://127.0.0.1:5000` manually.

## GitHub upload using only a browser
1. Sign in to GitHub and create a new **private** repository named `invoice-automation` (recommended while this is a prototype).
2. Extract this ZIP on your computer first. GitHub's browser uploader expects the files, not the ZIP itself, if you want the repository to show the source files.
3. In the new repository, select **Add file → Upload files**.
4. Upload `app.py`, `requirements.txt`, `README.md`, `start_windows.bat`, plus the `templates` and `static` folders and their contents.
5. Do not upload `.venv`, `invoice_app.db`, or real client invoices. The `uploads` folder is created automatically and should never contain client files in GitHub.
6. Commit the files.

GitHub browser upload may require uploading the folder contents rather than the folders themselves. If so, create `templates` and `static` in the repository via **Add file → Create new file** and use paths such as `templates/index.html`, then paste the relevant file contents. You can also use GitHub's web editor.

## Data and privacy
- Uploaded invoices and SQLite records are saved locally in this project folder.
- Do not upload real invoices, GSTINs, bank details or client accounting data to a public repository.
- This is a prototype, not a hardened production application. The development secret key should be changed before any broader use.
- Back up the project folder securely if you need to retain the records.

## Next development milestones
1. Add OCR extraction with a tested lightweight OCR engine.
2. Add deterministic validations (required fields, amount totals, date format and duplicate candidates).
3. Add a read-only Tally master-data connection and ledger-mapping screen.
4. Add a preview/approval gate and test Tally import on a separate test company.
