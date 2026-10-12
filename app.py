from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import sqlite3
import uuid
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "invoice_app.db"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.secret_key = "change-this-local-development-key"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB per file
UPLOAD_DIR.mkdir(exist_ok=True)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                doc_type TEXT DEFAULT 'Unknown',
                party_name TEXT DEFAULT '',
                gstin TEXT DEFAULT '',
                invoice_number TEXT DEFAULT '',
                invoice_date TEXT DEFAULT '',
                taxable_value TEXT DEFAULT '',
                tax_amount TEXT DEFAULT '',
                invoice_total TEXT DEFAULT '',
                ledger_name TEXT DEFAULT '',
                review_status TEXT DEFAULT 'Needs review',
                notes TEXT DEFAULT '',
                uploaded_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)


def log_action(conn, invoice_id, action, details=""):
    conn.execute(
        "INSERT INTO audit_log (invoice_id, action, details, created_at) VALUES (?, ?, ?, ?)",
        (invoice_id, action, details, datetime.now().isoformat(timespec="seconds"))
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    with db() as conn:
        invoices = conn.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
        total = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        needs_review = conn.execute(
            "SELECT COUNT(*) FROM invoices WHERE review_status != 'Approved'"
        ).fetchone()[0]
        approved = conn.execute(
            "SELECT COUNT(*) FROM invoices WHERE review_status = 'Approved'"
        ).fetchone()[0]
    return render_template("index.html", invoices=invoices, total=total,
                           needs_review=needs_review, approved=approved)


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("invoices")
    saved = 0
    for file in files:
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            flash(f"Skipped unsupported file: {file.filename}", "error")
            continue
        original_name = secure_filename(file.filename)
        stored_name = f"{uuid.uuid4().hex}_{original_name}"
        file.save(UPLOAD_DIR / stored_name)
        now = datetime.now().isoformat(timespec="seconds")
        with db() as conn:
            cur = conn.execute("""
                INSERT INTO invoices (original_name, stored_name, uploaded_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (original_name, stored_name, now, now))
            invoice_id = cur.lastrowid
            log_action(conn, invoice_id, "Uploaded", f"Original file: {original_name}")
        saved += 1
    if saved:
        flash(f"Uploaded {saved} file(s). OCR is not connected yet; review fields are manual in this starter version.", "success")
    return redirect(url_for("index"))


@app.route("/invoice/<int:invoice_id>", methods=["GET", "POST"])
def invoice_detail(invoice_id):
    with db() as conn:
        invoice = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        if invoice is None:
            flash("Invoice not found.", "error")
            return redirect(url_for("index"))
        if request.method == "POST":
            fields = {
                "doc_type": request.form.get("doc_type", "Unknown"),
                "party_name": request.form.get("party_name", "").strip(),
                "gstin": request.form.get("gstin", "").strip().upper(),
                "invoice_number": request.form.get("invoice_number", "").strip(),
                "invoice_date": request.form.get("invoice_date", "").strip(),
                "taxable_value": request.form.get("taxable_value", "").strip(),
                "tax_amount": request.form.get("tax_amount", "").strip(),
                "invoice_total": request.form.get("invoice_total", "").strip(),
                "ledger_name": request.form.get("ledger_name", "").strip(),
                "review_status": request.form.get("review_status", "Needs review"),
                "notes": request.form.get("notes", "").strip(),
            }
            now = datetime.now().isoformat(timespec="seconds")
            conn.execute("""
                UPDATE invoices SET doc_type=:doc_type, party_name=:party_name, gstin=:gstin,
                invoice_number=:invoice_number, invoice_date=:invoice_date,
                taxable_value=:taxable_value, tax_amount=:tax_amount, invoice_total=:invoice_total,
                ledger_name=:ledger_name, review_status=:review_status, notes=:notes, updated_at=:updated_at
                WHERE id=:id
            """, {**fields, "updated_at": now, "id": invoice_id})
            log_action(conn, invoice_id, "Saved review", f"Status: {fields['review_status']}; party: {fields['party_name'] or '(blank)'}")
            flash("Review saved. No Tally voucher was created.", "success")
            return redirect(url_for("invoice_detail", invoice_id=invoice_id))
        logs = conn.execute(
            "SELECT * FROM audit_log WHERE invoice_id = ? ORDER BY id DESC", (invoice_id,)
        ).fetchall()
    return render_template("detail.html", invoice=invoice, logs=logs)


@app.route("/file/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)


@app.route("/health")
def health():
    return {"status": "ok", "app": "local-invoice-review-starter", "tally_connected": False, "ocr_connected": False}


if __name__ == "__main__":
    init_db()
    print("Invoice Review Starter running at http://127.0.0.1:5000")
    print("This starter does not perform OCR or connect to Tally yet.")
    app.run(host="127.0.0.1", port=5000, debug=False)
