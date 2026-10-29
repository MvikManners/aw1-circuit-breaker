import mysql.connector

# Replace with YOUR database credentials from the PythonAnywhere 'Databases' tab
config = {
    'user': 'LavetoLab',
    'password': '19823Veks@@??',
    'host': 'LavetoLab.mysql.pythonanywhere-services.com',
    'database': 'LavetoLab$gospel_os' 
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # This command adds the column if it's missing
    cursor.execute("ALTER TABLE ghost_order ADD COLUMN category VARCHAR(50) DEFAULT 'MECHANICAL';")
    print("✅ SUCCESS: 'category' column added to ghost_order table.")
    
    conn.commit()
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
