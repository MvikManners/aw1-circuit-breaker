import imaplib
import email
from email.header import decode_header
import re
import google.generativeai as genai
import json
from datetime import datetime

# 🛡️ THE GOSPEL CORTEX CONFIG
# API Key integrated from Secure Studio
genai.configure(api_key="AIzaSyAjB69CP79fzdNAIFUeoalC_Ds4t4V1BFM") 
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_quote_with_ai(po_id, supplier_email, text_body):
    """The AI reads the email and returns a structured JSON quote."""

    prompt = f"""
    You are the Laveto Silk Road Negotiator. 
    Analyze this email from a supplier regarding Purchase Order LAV-SR-{po_id}.

    EXTRACT:
    1. Total Price (as a number only, ignore currency symbols).
    2. Estimated Delivery Time (in number of days).
    3. Supplier Name.

    EMAIL TEXT:
    {text_body}

    RETURN ONLY JSON in this format:
    {{"price": 1200.00, "days": 3, "supplier": "Name"}}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's pure JSON
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_json)

        # 💾 THE INJECTION: Save to your SilkRoadQuote table
        # We import here to avoid circular imports on PythonAnywhere
        from app import db, SilkRoadQuote

        new_quote = SilkRoadQuote(
            ghost_order_id=int(po_id),
            supplier_name=data['supplier'],
            price_quoted=float(data['price']),
            eta_days=int(data['days']),
            raw_reply=text_body[:500] 
        )
        db.session.add(new_quote)
        db.session.commit()

        print(f"✅ SUCCESS: Quote from {data['supplier']} logged for PO {po_id}")

    except Exception as e:
        print(f"🚨 AI ERROR: Could not parse email from {supplier_email}. Error: {e}")

# 🛡️ THE NEGOTIATOR: INBOX SCANNER
def check_supplier_replies():
    # ⚠️ Using the Secure App Password for command@laveto.net
    user = "command@laveto.net"
    password = "zojpxtrrmatvabvl" 

    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, password)
        mail.select("inbox")

        # Search for ALL unread emails
        status, messages = mail.search(None, 'UNSEEN')

        if not messages[0].split():
            print("📡 Negotiator: No new transmissions detected in inbox.")
            return

        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")
                    print(f"📡 Processing transmission from: {from_}")

                    # 🧠 LOGIC: Extract PO Number from Subject (LAV-SR-0004)
                    po_match = re.search(r"LAV-SR-(\d+)", subject)
                    if po_match:
                        po_id = po_match.group(1)
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                        else:
                            body = msg.get_payload(decode=True).decode()

                        # 🎯 TRIGGER THE AI CORTEX
                        analyze_quote_with_ai(po_id, from_, body)

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"🚨 CONNECTION ERROR: {e}")

if __name__ == "__main__":
    check_supplier_replies()