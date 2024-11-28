from flask import Blueprint

inventory = Blueprint('inventory', __name__)

from app.inventory import routes