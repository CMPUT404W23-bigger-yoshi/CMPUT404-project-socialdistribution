from pathlib import Path

from flask import Flask, jsonify, redirect, url_for
from flask.helpers import send_from_directory
from flask_swagger import swagger
from sqlalchemy import URL

# db must be initialized before importing models, that is what this import does
from api import bcrypt, db, login_manager
from api.admin import admin_bp
from api.swagger.swagger_bp import swaggerui_bp
from api.user import user_bp
from api.user.author import model
from api.user.author.model import Author
from api.user.comments import model
from api.user.followers import model
from api.user.posts import model

# Will need to use this later
url = URL.create("", username="", password="", host="", database="")  # dialect+driver


def create_app(testing_env=False):
    API_ROOT = "/api"
    REACT_BUILD_DIR = Path(__file__).parents[1] / "frontend" / "build"

    app = Flask(__name__, static_folder=REACT_BUILD_DIR)

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve(path):
        if not (REACT_BUILD_DIR / path).exists():
            # for anything that we don't recognize, it's likely a frontend path, so we can serve index.html
            # react will route according the path accordingly
            path = "index.html"
        # otherwise, we should be serving a frontend resource here
        return send_from_directory(app.static_folder, path)

    app.register_blueprint(user_bp, url_prefix=f"{API_ROOT}/authors")
    app.register_blueprint(admin_bp, url_prefix=f"{API_ROOT}/admin")
    app.register_blueprint(swaggerui_bp, url_prefix="/docs")

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

    @app.route("/spec")
    def spec():
        return jsonify(swagger(app))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
