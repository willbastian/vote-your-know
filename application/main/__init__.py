from flask import Blueprint

main = Blueprint('main', __name__)

# importing these views associate them with the blueprint!
from . import views
