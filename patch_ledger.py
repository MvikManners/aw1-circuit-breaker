import os
import urllib.parse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load credentials
load_dotenv()
db_user = os.getenv('DB_USER')
raw_pass = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
encoded_pass = urllib.parse.quote_plus(raw_pass) if raw_pass else ""

# Connect to the remote database
uri = f'mysql+pymysql://{db_user}:{encoded_pass}@LavetoLab.mysql.pythonanywhere-services.com/{db_name}'
engine = create_engine(uri)

# The missing date_created column
queries = [
    "ALTER TABLE sovereign_ledger ADD COLUMN date_created DATETIME DEFAULT CURRENT_TIMESTAMP;"
]

# Execute the patches
with engine.connect() as conn:
    for q in queries:
        try:
            conn.execute(text(q))
            print(f"✅ Executed: {q}")
        except Exception as e:
            print(f"⚠️ Error or already exists: {e}")
    conn.commit()

print("🏁 Ledger Patch Complete! You are ready to reload.")
