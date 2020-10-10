from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import pymysql

# Globally accessible libraries
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    # initalise application
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    # initilise plugins
    db.init_app(app)
    jwt.init_app(app)

    
    with app.app_context():
        # import parts of our application
        from . import token, crud, choose, submit

        app.register_blueprint(token.token_bp)
        app.register_blueprint(crud.crud_bp)
        app.register_blueprint(choose.choose_bp)
        app.register_blueprint(submit.submit_bp)

        return app
