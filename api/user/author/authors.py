import base64

from flask import Blueprint, request
from flask_login import current_user, login_required, login_user, logout_user

from api import bcrypt, db
from api.admin import APIConfig
from api.user.author.model import Author
from api.utils import get_pagination_params

# note: this blueprint is usually mounted under /authors URL prefix
authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/", methods=["GET"])
def get_authors():
    """
    Get all the authors
    ---
    responses:
      200:
        description: User created
    """
    authors = Author.query.paginate(**get_pagination_params().dict).items
    items = [author.getJSON() for author in authors]
    authors_json = {}
    authors_json["type"] = "authors"
    authors_json["items"] = items

    return authors_json


@authors_bp.route("/<string:author_id>", methods=["GET"])
def get_single_author(author_id: str):
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    return found_author.getJSON()


@authors_bp.route("/<string:author_id>", methods=["POST"])
@login_required
def update_author(author_id: str):
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    data = request.json
    displayName = data.get("displayName", None)
    github = data.get("github", None)
    host = data.get("host", None)
    profileImage = data.get("profileImage", None)

    if displayName:
        found_author.username = displayName
    if github:
        found_author.github = github
    if host:
        found_author.host = host
    if profileImage:
        found_author.profile_image = profileImage

    db.session.commit()
    return found_author.getJSON()


@authors_bp.route("/authenticated_user_id", methods=["GET"])
@login_required
def authenticated_user_id():
    if current_user.is_authenticated:
        auth_key = base64.b64encode((APIConfig.SELF_USERNAME + ":" + APIConfig.SELF_PASSWORD).encode("utf-8"))
        return {
            "id": current_user.id,
            "auth_key": auth_key.decode("utf-8"),
        }


@authors_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"message": "Success"}, 200


@authors_bp.route("/login", methods=["POST"])
def login():
    # todo make it a redirect
    if current_user.is_authenticated:
        return {"message": "Already logged in"}

    data = request.json
    username = data.get("username", None)
    password = data.get("password", None)

    if username is None or password is None:
        return {"message": "Invalid Credentials"}, 400  # bad request

    # todo we can handle the error client side to make
    user = Author.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return {"message": "Invalid credentials"}, 401

    login_user(user)

    auth_key = base64.b64encode((APIConfig.SELF_USERNAME + ":" + APIConfig.SELF_PASSWORD).encode("utf-8"))

    # todo redirect hello
    return {
        "message": "Success",
        "auth_key": auth_key.decode("utf-8"),
    }, 200


@authors_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username", None)
    password = data.get("password", None)

    if not username or not password:
        return {"message": "Invalid Credentials"}, 400  # bad request

    # todo we can handle the error client side to make
    user_exists = Author.query.filter_by(username=username).first()
    if user_exists:
        # username already exists
        return {"message": "User Already exists"}, 409

    user = Author(username=username, password=bcrypt.generate_password_hash(password).decode("utf-8"), host="bigger")
    db.session.add(user)
    db.session.commit()
    login_user(user)

    # todo redirect
    return {"message": "Success"}, 200
