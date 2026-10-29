path = '/home/LavetoLab/templates/ledger.html'
with open(path, 'r') as f:
    data = f.read()

# Explicitly stripping the namespace that is causing your 500 errors
fixed_data = data.replace("url_for('hangar.registry')", "url_for('registry')")
fixed_data = fixed_data.replace("url_for('hangar.silk_road')", "url_for('silk_road')")
fixed_data = fixed_data.replace("url_for('hangar.open_bay_01')", "url_for('open_bay_01')")
fixed_data = fixed_data.replace("url_for('hangar.settings')", "url_for('settings')")

with open(path, 'w') as f:
    f.write(fixed_data)
print("Routes sanitized.")