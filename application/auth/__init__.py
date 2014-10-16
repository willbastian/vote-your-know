from flask import Blueprint

auth = Blueprint('auth', __name__, static_folder='../static')

# importing these views associate them with the blueprint!
from . import views
