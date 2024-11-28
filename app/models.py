from app import db, bcrypt
from flask_login import UserMixin

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