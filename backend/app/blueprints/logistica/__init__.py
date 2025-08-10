from flask import Blueprint

logistica_bp = Blueprint('logistica', __name__)

from . import routs