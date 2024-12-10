from app import db, bcrypt
from flask_login import UserMixin
from datetime import datetime, timezone

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    # def set_password(self, password):
    #     #hash and set the user's password
    #     self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    # def check_password(self, password):
    #     return bcrypt.check_password_hash(self.password_hash, password)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), nullable=False, default=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(50), nullable=True)
    categories = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f"Inventory('{self.name}', '{self.price}', '{self.quantity}')"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")
    total = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Float, nullable=False, default=0.0)  # Amount already paid
    due = db.Column(db.Float, nullable=False)  # Remaining amount (calculated as total - paid)
    created_by = db.Column(db.String(50), nullable=False)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)
    
class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)