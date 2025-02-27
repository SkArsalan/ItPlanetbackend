from flask import Blueprint

purchase = Blueprint('purchase', __name__)
from app.purchase import routes