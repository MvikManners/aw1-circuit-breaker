# core/services/cellulant_payouts.py
import os
import requests
from datetime import datetime

CELLULANT_BASE_URL = os.environ.get('CELLULANT_BASE_URL', 'https://api.tingg.africa')
CELLULANT_SANDBOX_MODE = os.environ.get('CELLULANT_SANDBOX_MODE', 'True').lower() in ['true', '1', 'yes']
CELLULANT_USERNAME = os.environ.get('CELLULANT_USERNAME', '').strip()
CELLULANT_PASSWORD = os.environ.get('CELLULANT_PASSWORD', '').strip()
CELLULANT_HUB_ID = os.environ.get('CELLULANT_HUB_ID', 'LAVETO_BWP_HUB')

def trigger_cellulant_payout(destination_phone, amount, currency='BWP', country_code='BW', narration='Laveto Admin Profit Sweep'):
    timestamp_str = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    payer_tx_id = f"LVT-PAYOUT-{timestamp_str}"

    # 🧪 SAFE SANDBOX / SIMULATION MODE (No real charges or funds moved)
    if CELLULANT_SANDBOX_MODE or not CELLULANT_USERNAME:
        print(f"\n--- [CELLULANT SANDBOX PAYOUT TEST] ---", flush=True)
        print(f"Mode: SAFE SANDBOX (Zero Real Charges)")
        print(f"Destination: {destination_phone}")
        print(f"Amount: P{float(amount):,.2f} {currency}")
        print(f"Generated Ref: {payer_tx_id}")
        print(f"-----------------------------------------\n", flush=True)

        return {
            "success": True,
            "reference": payer_tx_id,
            "message": f"Sandbox Test Payout of P{float(amount):,.2f} processed successfully (No charges incurred)."
        }

    # 🌐 LIVE PRODUCTION API DISPATCH (When Sandbox Mode is False)
    endpoint = f"{CELLULANT_BASE_URL}/v1/global-api/payments"
    payload = {
        "function": "BEEP.postPayment",
        "countryCode": country_code,
        "payload": {
            "credentials": {
                "username": CELLULANT_USERNAME,
                "password": CELLULANT_PASSWORD
            },
            "packet": {
                "serviceCode": "MOBILE-MONEY-B2C",
                "MSISDN": destination_phone,
                "accountNumber": destination_phone,
                "payerTransactionID": payer_tx_id,
                "amount": float(amount),
                "datePaymentReceived": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "currencyCode": currency,
                "countryCode": country_code,
                "narration": narration,
                "invoiceNumber": payer_tx_id,
                "hubID": CELLULANT_HUB_ID,
                "paymentMode": "Mobile Money",
                "pushToOriginator": True
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        res_data = response.json()

        auth_status = res_data.get('authStatus', {})
        status_code = auth_status.get('authStatusCode') or res_data.get('statusCode')

        if response.status_code in [200, 201] and str(status_code) in ['0', '00', 'SUCCESS', '200']:
            return {
                "success": True,
                "reference": payer_tx_id,
                "gateway_response": res_data,
                "message": "Payout successfully posted to Cellulant."
            }
        else:
            return {
                "success": False,
                "reference": payer_tx_id,
                "gateway_response": res_data,
                "message": res_data.get('message') or f"Cellulant payout rejected with code: {status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "reference": payer_tx_id,
            "message": f"Network exception communicating with Cellulant: {str(e)}"
        }