from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from core.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='AGENT')
    payable_balance = db.Column(db.Float, default=0.0)

    # 🟢 Vault Columns
    equity_reserve = db.Column(db.Float, default=0.0)
    shield_reservoir = db.Column(db.Float, default=0.0)
    total_contributions = db.Column(db.Float, default=0.0)

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

class HubPartner(db.Model):
    __tablename__ = 'hub_partners'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    successful_audits = db.Column(db.Integer, default=0)

class Warden(db.Model):
    __tablename__ = 'warden'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    warden_id = db.Column(db.String(50), unique=True, nullable=False) # e.g., WARDEN-01
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200))
    wallet_balance = db.Column(db.Float, default=0.0)

    @property
    def referral_link(self):
        domain = request.url_root.rstrip('/')
        return f"{domain}/apply?ref={self.warden_id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)