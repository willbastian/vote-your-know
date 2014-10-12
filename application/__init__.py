from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
import logging

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name):
    logging.debug('start create app')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    logging.debug('APP CONFIG: ' + str(app.config))

    config[config_name].init_app(app)  # does nothing, for now
    bootstrap.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    logging.debug('end create app')
    return app
