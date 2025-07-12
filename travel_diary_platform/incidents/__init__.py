from flask import Blueprint

incidents_bp = Blueprint('incidents', __name__)

from incidents import routes
