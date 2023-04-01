import json
import os
from pathlib import Path

from flasgger import Swagger
from flask import Flask, jsonify, redirect, url_for
from flask.helpers import send_from_directory
from flask_admin import Admin
from flask_cors import CORS
from sqlalchemy import URL

import api.user.followers.model
from api import API_ROOT, basic_auth, bcrypt, db, login_manager
from api.admin.actions import actions_bp
from api.admin.APIAuth import APIAuth
from api.admin.APIConfig import APIConfig
from api.admin.inbound_connection import InboundConnection, InboundConnectionView
from api.admin.nodes import nodes_bp
from api.admin.outbound_connection import OutboundConnection, OutboundConnectionView
from api.admin.post_admin import PostView
from api.admin.user_account_control import UserAccountControlView
from api.admin.views import Logout, SettingsView
from api.user.author.model import Author
from api.user.comments.model import Comment
from api.user.posts.model import Post
from api.user.user import user_bp

# Will need to use this later
url = URL.create("", username="", password="", host="", database="")  # dialect+driver


def create_app(testing_env=False):
    REACT_BUILD_DIR = Path(__file__).parents[1] / "frontend" / "build"

    app = Flask(__name__, static_folder=REACT_BUILD_DIR)
    CORS(app)

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve(path):
        if not (REACT_BUILD_DIR / path).exists():
            # for anything that we don't recognize, it's likely a frontend path, so we can serve index.html
            # react will route according the path accordingly
            path = "index.html"
        # otherwise, we should be serving a frontend resource here
        return send_from_directory(app.static_folder, path)

    ADMIN_ENDPOINT = f"{API_ROOT}/admin/action"

    app.register_blueprint(user_bp, url_prefix=f"{API_ROOT}/authors")
    app.register_blueprint(nodes_bp, url_prefix=f"{API_ROOT}/nodes")
    app.register_blueprint(actions_bp, url_prefix=ADMIN_ENDPOINT)

    app.config.from_object("api.config.Config")

    if testing_env:
        app.config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///testing.db"})

    basic_auth.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # admin views
    admin = Admin(app, name="bigger-yoshi", template_mode="bootstrap3")
    admin.add_view(SettingsView(name="Settings", endpoint="settings"))
    admin.add_view(UserAccountControlView(Author, db.session, name="User Account Control", endpoint="accounts"))
    admin.add_view(PostView(Post, db.session, name="Posts", endpoint="posts"))
    admin.add_view(
        OutboundConnectionView(
            OutboundConnection, db.session, name="Outbound server connections", endpoint="connections"
        )
    )
    admin.add_view(
        InboundConnectionView(
            InboundConnection, db.session, name="Inbound server connections", endpoint="connections_inbound"
        )
    )
    admin.add_view(Logout(name="logout", endpoint="Logout"))
    app.jinja_env.globals.update(APIConfig=APIConfig, admin_endpoint=ADMIN_ENDPOINT)

    # docs
    p = Path(__file__).with_name("swagger.json")
    with p.open("r") as file:
        template = json.load(file)
        Swagger(app, template=template)

    @login_manager.user_loader
    def load_user(author_id):
        return Author.query.filter(Author.id == author_id).first()

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
