from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
print('after db')


def create_app(config_name):
    print('start create_app')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    print(app.config)
    config[config_name].init_app(app)  # does nothing, for now

    print("bootstrap init")
    bootstrap.init_app(app)
    print("db init")
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    print('end create_app')
    return app
