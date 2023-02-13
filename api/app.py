from flask import Flask, redirect, url_for

from api import db
from api.admin import admin_bp
from api.user import user_bp
from api.user.author import model
from api.user.comments import model
from api.user.posts import model

# db must be initialized before importing models


# note: Heroku will run things from the working directory as the root of this repo. Therefore, this path MUST
# be relative to the root of the repo, NOT to this file. You will likely need to specify the working directory
# as the root of this repo # when you run this file in your IDE


def create_app():
    app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
    app.register_blueprint(user_bp, url_prefix="/authors")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bigger_yoshi1.db"

    db.init_app(app)

    with app.app_context():
        db.create_all()
    return app
