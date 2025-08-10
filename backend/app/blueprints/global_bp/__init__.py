from flask import Blueprint

global_bp = Blueprint('global', __name__, url_prefix='/')

from . import routs