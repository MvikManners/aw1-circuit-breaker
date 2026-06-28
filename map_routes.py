# Save as map_routes.py
from core.app import app
print("--- REGISTERED ROUTES ---")
for rule in app.url_map.iter_rules():
    print(f"Endpoint: {rule.endpoint} | Path: {rule.rule}")