import os
from flask import Flask
from views import BlueprintHealth, BlueprintPost, BlueprintReset
from db import db

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')


def create_app(database=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = database or \
      f'postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(BlueprintHealth, url_prefix='/posts')
    app.register_blueprint(BlueprintPost)
    app.register_blueprint(BlueprintReset)

    return app
