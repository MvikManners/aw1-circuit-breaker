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

# The missing columns for the ghost_order table
queries = [
    "ALTER TABLE ghost_order ADD COLUMN category VARCHAR(50);",
    "ALTER TABLE ghost_order ADD COLUMN grade INTEGER DEFAULT 1;",
    "ALTER TABLE ghost_order ADD COLUMN oem_part_number VARCHAR(100);",
    "ALTER TABLE ghost_order ADD COLUMN tier1_brand VARCHAR(100);",
    "ALTER TABLE ghost_order ADD COLUMN supplier VARCHAR(100);",
    "ALTER TABLE ghost_order ADD COLUMN shipping_routing VARCHAR(100);",
    "ALTER TABLE ghost_order ADD COLUMN wholesale_cost FLOAT DEFAULT 0.0;",
    "ALTER TABLE ghost_order ADD COLUMN estimated_cost FLOAT DEFAULT 0.0;",
    "ALTER TABLE ghost_order ADD COLUMN estimated_arrival DATETIME;",
    "ALTER TABLE ghost_order ADD COLUMN date_logged DATETIME DEFAULT CURRENT_TIMESTAMP;"
]

# Execute the patches
with engine.connect() as conn:
    for q in queries:
        try:
            conn.execute(text(q))
            print(f"✅ Executed: {q}")
        except Exception as e:
            print(f"⚠️ Skipped (already exists): {q.split('ADD COLUMN ')[1].split(' ')[0]}")
    conn.commit()

print("🏁 Ghost Order Patch Complete! You are ready to reload.")

