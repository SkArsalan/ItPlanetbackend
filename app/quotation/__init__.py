from flask import Blueprint
quotation = Blueprint('quotation', __name__)

from app.quotation import routes