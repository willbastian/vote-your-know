from flask import Blueprint
print ('before blueprint')
main = Blueprint('main', __name__)
print ('after blueprint')
from . import views
