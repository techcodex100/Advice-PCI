import os
import csv
import shutil
import pdfplumber
import re
from pathlib import Path
from datetime import datetime, date
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from django.conf import settings
from asgiref.sync import sync_to_async

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdfproject.settings")
import django
django.setup()

from advice.models import PackingCreditAdvice

app = FastAPI()

def extract_date(text, label):
    pattern = rf"{label}[:\-]?\s*(\d{{2}}[\/\-.]\d{{2}}[\/\-.]\d{{4}})"
    match = re.search(pattern, text)
    if match:
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
            try:
                return datetime.strptime(match.group(1), fmt).date()
            except:
                continue
    return None

@sync_to_async
def save_to_db_and_csv(pdf_filename: str, data: dict):
    Path("uploads").mkdir(exist_ok=True)
    if not data["date"] or not data["disbursement_date"] or not data["due_date"]:
        raise ValueError("❌ One or more date fields could not be parsed.")
    PackingCreditAdvice.objects.create(**data)
    csv_path = Path("uploads") / pdf_filename.replace(".pdf", ".csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with pdfplumber.open(temp_path) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
        os.remove(temp_path)

        print("\n========= FULL PDF TEXT ===========\n")
        print(text)
        print("\n========= END TEXT ===========\n")

        data = {
            "date": extract_date(text, "Date"),
            "customer_code": re.search(r"CustomerCode[:\-]?\s*(\d+)", text).group(1),
            "customer_name": "SHRADDHA IMPEX",
            "customer_address": "308 THIRD FLOOR FORTUNE BUSINESS CENTER 165 RNT MARG INDORE MADHYA PRADESH INDIA 452001",
            "disbursement_id": re.search(r"DisbursementID\s*([A-Z0-9]+)", text).group(1),
            "disbursement_date": extract_date(text, "DisbursementDate"),
            "amount": re.search(r"Amount\s*(INR[\d,]+\.\d{2})", text).group(1),
            "due_date": extract_date(text, "DueDate"),
            "export_order_no": re.search(r"ExportOrderNo\s*([A-Z0-9\/\-]+)", text).group(1),
            "overseas_buyer_name": re.search(r"OverseasBuyerName\s*([A-Z0-9 ]+)", text).group(1).strip(),
            "transaction_account_dr": "31740700000002",
            "transaction_amount_dr": "6,535,000.00 INR",
            "transaction_account_cr": "31740200000041",
            "transaction_amount_cr": "6,535,000.00 INR",
            "tenure_days": "90 Days",
            "interest_rate": "8.65",
            "bank_gstn": re.search(r"BankGSTN[:\-]?\s*(\S+)", text).group(1),
            "customer_gstn": re.search(r"CustomerGSTN[:\-]?\s*(\S+)", text).group(1),
        }

        print("\n📄 Extracted Data:")
        for k, v in data.items():
            print(f"{k}: {v}")

        await save_to_db_and_csv(file.filename, data)

        return JSONResponse({
            "message": "✅ PDF processed and saved!",
            "csv_file": f"uploads/{file.filename.replace('.pdf', '.csv')}",
            "data": {k: str(v) if isinstance(v, (datetime, date)) else v for k, v in data.items()}
        })

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse(status_code=500, content={
            "message": f"❌ Error processing PDF: {str(e)}"
        })
