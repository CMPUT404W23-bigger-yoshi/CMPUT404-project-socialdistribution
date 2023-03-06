from flask import Flask, redirect, url_for
from flask.helpers import send_from_directory
from sqlalchemy import URL

from api import bcrypt, db, login_manager
from api.admin import admin_bp
from api.user import user_bp
from api.user.author import model
from api.user.author.model import Author
from api.user.comments import model
from api.user.followers import model
from api.user.posts import model

# db must be initialized before importing models


# note: Heroku will run things from the working directory as the root of this repo. Therefore, this path MUST
# be relative to the root of the repo, NOT to this file. You will likely need to specify the working directory
# as the root of this repo # when you run this file in your IDE

# Will need to use this later
url = URL.create("", username="", password="", host="", database="")  # dialect+driver


def create_app(testing_env=False):
    app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")

    @app.route("/")
    def serve():
        return send_from_directory(app.static_folder, "index.html")

    # note: Heroku will run things from the working directory as the root of this repo. Therefore, this path MUST
    # be relative to the root of the repo, NOT to this file. You will likely need to specify the working directory
    # as the root of this repo # when you run this file in your IDE
    app.register_blueprint(user_bp, url_prefix="/authors")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    app.config.from_object("api.config.Config")

    if testing_env:
        app.config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///testing.db"})

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(author_id):
        return Author.query.filter(Author.id == author_id).first()

    with app.app_context():
        db.create_all()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
