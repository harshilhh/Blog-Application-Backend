from flask import Flask , jsonify
from models.schema import db
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


    # blueprint
    from models.schema import core_models
    app.register_blueprint(core_models)

    from api.formprocesser import api
    app.register_blueprint(api)

    return app