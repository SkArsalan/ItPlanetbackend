from flask import Blueprint

citation = Blueprint('citation', __name__)

from app.citation import routes