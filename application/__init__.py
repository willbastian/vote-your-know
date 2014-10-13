from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
import logging

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    logging.debug('start application factory (create_app).....')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    logging.debug('APP CONFIG: ' + str(app.config))

    config[config_name].init_app(app)  # does nothing, for now
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    logging.debug('.....end application factory (create_app)')
    return app
