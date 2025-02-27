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
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(50), nullable=True)
    categories = db.Column(db.String(50),db.ForeignKey('section.categories', ondelete='CASCADE'), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    def __repr__(self):
        return f"Inventory('{self.name}', '{self.price}', '{self.quantity}')"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")
    total = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Float, nullable=False, default=0.0)  # Amount already paid
    due = db.Column(db.Float, nullable=False)  # Remaining amount (calculated as total - paid)
    created_by = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=True)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")
    
class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id', ondelete='SET NULL'), nullable=True)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    categories = db.Column(db.String(50),db.ForeignKey('section.categories', ondelete='CASCADE'), nullable=True)  # Changed from 'category' to 'categories'
    quantity = db.Column(db.Integer, nullable=False)  # Changed from 'qty' to 'quantity'
    selling_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    
    def calculate_profit(self):
        inventory_item = Inventory.query.get(self.item_id)
        if inventory_item:
            return (self.selling_price - inventory_item.purchase_price) * self.quantity  # Adjusted for 'quantity'
        return 0.0
    
    def set_profit(self):
        self.profit = self.calculate_profit()

        
class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    quotation_number = db.Column(db.String(100), unique=True, nullable=False)
    categories = db.Column(db.String(50), 
                           db.ForeignKey('section.categories', ondelete='CASCADE'),
                           nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    quotation_date = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=True)
    quotation_items = db.relationship(
        'QuotationItem', 
        backref='quotation', 
        lazy=True, 
        cascade="all, delete-orphan", 
        foreign_keys='QuotationItem.quotation_id'  # Specify the foreign key column
    )
class QuotationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sub_total = db.Column(db.Float, nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id', ondelete='CASCADE'), nullable=False)  # Cascade delete for Quotation
    quotation_number = db.Column(db.String(100), db.ForeignKey('quotation.quotation_number', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))

class Purchase(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    supplier_name = db.Column(db.String(50), nullable=False)
    purchase_number = db.Column(db.String(100), unique=True, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")
    total = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Float, nullable=False, default=0.0)  # Amount already paid
    due = db.Column(db.Float, nullable=False)  # Remaining amount (calculated as total - paid)
    created_by = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=True)
    purchase_items = db.relationship(
       'PurchaseItem', 
        backref='purchase', 
        lazy=True, 
        cascade="all, delete-orphan", 
        foreign_keys='PurchaseItem.purchase_id'  # Specify the foreign key column
    )
    
class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sub_total = db.Column(db.Float, nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id', ondelete='CASCADE'), nullable=False)  # Cascade delete for purchase
    purchase_number = db.Column(db.String(100), db.ForeignKey('purchase.purchase_number', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categories = db.Column(db.String(50), nullable=False, unique=True)