from app import app, db
from app import User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Initiating Agent Protocol...")

    # 1. Search the database for the agent
    agent = User.query.filter_by(username='agent_k').first()

    if agent:
        print("Agent found! Resetting password to laveto2026...")
        agent.password_hash = generate_password_hash('laveto2026')
        agent.role = 'AGENT'
    else:
        print("Creating brand new Field Agent...")
        agent = User(
            username='agent_k',
            password_hash=generate_password_hash('laveto2026'),
            role='AGENT'
        )
        db.session.add(agent)

    db.session.commit()
    print("✅ Field Agent [agent_k] is officially active.")
