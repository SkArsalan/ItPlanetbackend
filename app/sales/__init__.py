from flask import Blueprint

sales = Blueprint('sales', __name__)

from app.sales import routes