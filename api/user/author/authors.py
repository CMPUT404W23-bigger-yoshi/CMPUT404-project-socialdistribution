import base64

from flasgger import swag_from
from flask import Blueprint, request
from flask_login import current_user, login_required, login_user, logout_user

from api import basic_auth, bcrypt, db
from api.admin.APIConfig import APIConfig
from api.user.author.docs import author_schema, authors_schema
from api.user.author.model import Author
from api.utils import Approval, get_pagination_params

# note: this blueprint is usually mounted under /authors URL prefix
authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/", methods=["GET"])
@swag_from(
    {
        "description": "Returns list of authors",
        "responses": {200: {"description": "A List of authors", "schema": authors_schema}},
    }
)
@basic_auth.required
def get_authors():
    authors = Author.query.paginate(**get_pagination_params().dict).items
    items = [author.getJSON() for author in authors]
    authors_json = {}
    authors_json["type"] = "authors"
    authors_json["items"] = items

    return authors_json


@authors_bp.route("/<string:author_id>", methods=["GET"])
@swag_from(
    {
        "description": "Returns an Author with id",
        "parameters": [
            {"name": "author_id", "type": "string", "required": "true", "description": "The id of author to retrieve"}
        ],
        "responses": {200: {"description": "Returns a single author", "schema": author_schema}},
    }
)
@basic_auth.required
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
        return {
            "id": current_user.id,
        }, 200


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

    if user.approval == Approval.PENDING:
        return {"message": "Author approval pending"}, 401

    login_user(user)

    # todo redirect hello
    return {
        "message": "Success",
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
