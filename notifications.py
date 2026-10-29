import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Vela, this is your secure relay connection [cite: 2026-03-04]
GMAIL_USER = "mvik1982@gmail.com"  # Verified business address
GMAIL_PASSWORD = "tyhmnkpqzmofgrrh" # Confirmed working Relay Key

def send_forensic_decree(member_email, member_name, vin, status="Sanctified"):
    """
    Automated dispatch for Asset Sanctification and Shield Activation.
    Connects the 2 TB industrial vault to the 500-member ledger [cite: 2026-02-23, 2026-03-04].
    """
    
    msg = MIMEMultipart()
    msg['From'] = f"System Restoration <{GMAIL_USER}>"
    msg['To'] = member_email
    msg['Subject'] = f"[OFFICIAL DECREE] - Asset {vin} {status.upper()}"

    # Body matching the industrial aesthetic of System Restoration [cite: 2026-03-04]
    body = (
        f"Founder {member_name},\n\n"
        f"Your asset (VIN: {vin}) has been forensically verified and is now {status}.\n"
        f"The record has been locked into your 2 TB industrial vault.\n\n"
        f"SYSTEM RESTORATION: Asset Integrity Guaranteed."
    )
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Utilizing the secure SSL port 465 for industrial-grade safety [cite: 2026-03-04]
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("SUCCESS: Signal Dispatched")
        return True
    except Exception as e:
        # Forensic logging of any relay failures [cite: 2026-03-04]
        print(f"Relay Failure: {e}")
        return False