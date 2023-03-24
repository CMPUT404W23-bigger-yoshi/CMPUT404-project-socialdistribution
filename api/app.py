from flask import Flask, jsonify, redirect, url_for
from flask.helpers import send_from_directory
from flask_admin import Admin
from flask_swagger import swagger
from sqlalchemy import URL

import api.user.followers.model
from api import basic_auth, bcrypt, db, login_manager
from api.admin.actions import actions_bp
from api.admin.APIAuth import APIAuth
from api.admin.APIConfig import APIConfig
from api.admin.model import AuthAdmin, Connection, ConnectionAdmin
from api.admin.nodes import nodes_bp
from api.admin.views import Logout, SettingsView
from api.swagger.swagger_bp import swaggerui_blueprint
from api.user.author.model import Author
from api.user.comments.model import Comment
from api.user.posts.model import Post
from api.user.user import user_bp

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
    app.register_blueprint(nodes_bp, url_prefix="/nodes")
    app.register_blueprint(actions_bp, url_prefix="/admin/action")
    app.register_blueprint(swaggerui_blueprint, url_prefix="/docs")

    app.config.from_object("api.config.Config")

    if testing_env:
        app.config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///testing.db"})

    basic_auth.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # admin views
    admin = Admin(app, name="bigger-yoshi", template_mode="bootstrap3")
    admin.add_view(AuthAdmin(Author, db.session))
    admin.add_view(ConnectionAdmin(Connection, db.session))
    admin.add_view(SettingsView(name="Settings", endpoint="settings"))
    admin.add_view(Logout(name="logout", endpoint="Logout"))
    app.jinja_env.globals.update(APIConfig=APIConfig)

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
