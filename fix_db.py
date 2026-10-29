import mysql.connector

try:
    db = mysql.connector.connect(
        host="LavetoLab.mysql.pythonanywhere-services.com",
        user="LavetoLab",
        password="YOUR_DATABASE_PASSWORD_HERE",
        database="LavetoLab$gospel_os" 
    )
    cursor = db.cursor()
    # Adding the column
    cursor.execute("ALTER TABLE ghost_order ADD COLUMN category VARCHAR(50) DEFAULT 'MECHANICAL';")
    print("✅ Success! Column 'category' added to ghost_order table.")
except Exception as e:
    print(f"❌ Error: {e}")

