from flask import Flask, render_template_string
import pandas as pd
import os

app = Flask(__name__)
BASE_DIR = '/home/LavetoLab/'

@app.route('/')
def home():
    try:
        # 1. Pull Data from Brain
        df = pd.read_csv(os.path.join(BASE_DIR, 'members_list.csv'))
        count = len(df[df['Role'].str.strip().str.lower() == 'member'])
        remaining = 500 - count
        
        # 2. Polished Dashboard Design
        return render_template_string("""
        <html>
            <head>
                <title>Laveto Hub</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; text-align: center; background-color: #f4f7f6; padding: 50px; }
                    .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: inline-block; border-top: 10px solid #2c3e50; min-width: 350px; }
                    .admin-badge { background: #2c3e50; color: white; padding: 6px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
                    .status-dot { color: #27ae60; font-weight: bold; margin-bottom: 20px; }
                    .btn { display: inline-block; margin-top: 25px; padding: 12px 30px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: 0.3s; }
                    .btn:hover { background: #2980b9; transform: translateY(-2px); }
                    .stat-box { background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; }
                </style>
            </head>
            <body>
                <div class="card">
                    <span class="admin-badge">Architect Access: Vela</span>
                    <h1 style="margin-top:20px; color:#2c3e50;">LAVETO: SYSTEM RESTORATION</h1>
                    <p class="status-dot">● ONLINE HUB ACTIVE</p>
                    <hr style="border:0; border-top:1px solid #eee;">
                    
                    <div class="stat-box">
                        <p style="margin:5px 0; color:#7f8c8d;">Cooperative Capacity</p>
                        <h2 style="margin:0; color:#2c3e50;">{{ c }} / 500</h2>
                    </div>

                    <div class="stat-box">
                        <p style="margin:5px 0; color:#7f8c8d;">Available Slots</p>
                        <h2 style="margin:0; color:#27ae60;">{{ r }}</h2>
                    </div>

                    <a href="/registry" class="btn">OPEN MEMBER REGISTRY</a>
                </div>
            </body>
        </html>
        """, c=count, r=remaining)
    except Exception as e:
        return f"<h1>Hub Offline</h1><p>Error: {e}</p>"

@app.route('/registry')
def registry():
    try:
        df = pd.read_csv(os.path.join(BASE_DIR, 'members_list.csv'))
        table_html = df.to_html(classes='table', index=False)
        return render_template_string("""
        <html>
            <head>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; padding: 40px; background: #f4f7f6; }
                    .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
                    .table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    .table th { background: #2c3e50; color: white; padding: 12px; text-align: left; }
                    .table td { padding: 12px; border-bottom: 1px solid #eee; }
                    .btn-back { display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #7f8c8d; color: white; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>MEMBER REGISTRY</h1>
                    <a href="/" class="btn-back">← Back to Dashboard</a>
                    <div style="overflow-x:auto;">{{ t|safe }}</div>
                </div>
            </body>
        </html>
        """, t=table_html)
    except Exception as e:
        return f"<h1>Registry Error</h1><p>{e}</p>"