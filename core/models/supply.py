from core.extensions import db

class SovereignSupplyInventory(db.Model):
    __tablename__ = 'sovereign_supply_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    sku_code = db.Column(db.String(100), unique=True, nullable=False)
    
    # Inventory Tracking
    stock_quantity = db.Column(db.Integer, default=0)
    
    # Financial Mapping
    base_production_cost = db.Column(db.Float, default=0.0)
    member_retail_price = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<SovereignSupply {self.sku_code}: {self.item_name}>"