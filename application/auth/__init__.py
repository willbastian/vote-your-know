from flask import Blueprint

auth = Blueprint('auth', __name__)

# importing these views associate them with the blueprint!
from . import views
