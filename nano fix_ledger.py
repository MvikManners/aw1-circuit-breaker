import re

template_path = '/home/LavetoLab/templates/ledger.html'

with open(template_path, 'r') as f:
    content = f.read()

# Define routes that MUST be root-level (do not add 'hangar.' prefix)
root_routes = ['static', 'view_ledger', 'registry', 'master_registry']

def replace_url(match):
    full_call = match.group(0)
    route_name = match.group(1)

    
    # If it's a root route, ensure it's clean
    if route_name in root_routes:
        return f"url_for('{route_name}')"
    # If it's already namespaced, leave it
    elif route_name.startswith('hangar.'):
        return full_call
    # Otherwise, apply the required namespace
    else:
        return f"url_for('hangar.{route_name}')"

# Regex to find url_for('route_name')
new_content = re.sub(r"url_for\('([^']+)'\)", replace_url, content)

with open(template_path, 'w') as f:
    f.write(new_content)

print("Template synchronization complete.")