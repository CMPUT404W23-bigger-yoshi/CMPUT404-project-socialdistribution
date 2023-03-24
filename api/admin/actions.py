from flask import Blueprint, current_app, redirect, request
from flask_login import current_user, login_required, login_user

from api import bcrypt, db
from api.admin.APIAuth import Connection
from api.admin.APIConfig import APIConfig
from api.user.author.model import Author
from api.utils import Approval, Role

actions_bp = Blueprint("actions", __name__)


@actions_bp.route("/login", methods=["POST"])
def login_admin():
    form_data = request.form

    username = form_data.get("username")
    password = form_data.get("password")

    print(username, password)
    if not username or not password:
        return {"message": "Invalid Credentials"}, 400

    user = Author.query.filter_by(username=username).first()

    if not user or not user.role == Role.ADMIN or not bcrypt.check_password_hash(user.password, password):
        return {"message": "Incorrect credentials"}, 401

    if user.approval == Approval.PENDING:
        return {"message": "User not approved"}, 401

    login_user(user)

    return {"message": "login success"}, 200


@actions_bp.route("/config", methods=["POST"])
@login_required
def modify_config():
    if not (current_user.is_authenticated and current_user.role == Role.ADMIN):
        return {"message": "Admin login required."}, 401

    form_data = request.form

    api_protect = form_data.get("API")
    author_auto = form_data.get("Approve-authors")
    nodes_auto = form_data.get("Approve-nodes")
    node_limit = form_data.get("Node-limit")

    if api_protect:
        APIConfig.set_API_protection(True)
    else:
        APIConfig.set_API_protection(False)

    if author_auto:
        APIConfig.set_author_approval(True)
    else:
        APIConfig.set_author_approval(False)

    if nodes_auto:
        APIConfig.set_node_approval(True)
    else:
        APIConfig.set_node_approval(False)

    if node_limit:
        val = int(node_limit)
        if val >= 0:
            APIConfig.set_node_limit(val)

    return {"message": "Success"}, 200
