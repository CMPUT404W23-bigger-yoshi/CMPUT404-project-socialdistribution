from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from api import bcrypt, db
from api.user.author.model import Author
from api.utils import get_pagination_params

# note: this blueprint is usually mounted under /authors URL prefix
authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/", methods=["GET"])
def get_authors():
    args = request.args
    authors = Author.query.paginate(**get_pagination_params().as_dict).items
    return jsonify(authors)


@authors_bp.route("/admin", methods=["POST"])
def create_author():
    """
    Endpoint for Only Testing purposes
    """
    data = request.json
    displayName = data.get("displayName", None)
    github = data.get("github", None)
    host = data.get("host", None)
    profileImage = data.get("profileImage", None)

    author_to_add = Author(username=displayName, github=github, host=host, profile_image=profileImage)
    db.session.add(author_to_add)
    db.session.commit()
    return {"Success": 1}


@authors_bp.route("/<string:author_id>", methods=["GET"])
def get_single_author(author_id: str):
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    return jsonify(found_author)


@authors_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Success"}), 200


@authors_bp.route("/login", methods=["POST"])
def login():
    # todo make it a redirect
    if current_user.is_authenticated:
        return jsonify({"message": "Already logged in"})

    data = request.json
    username = data.get("username", None)
    password = data.get("password", None)

    if username is None or password is None:
        return jsonify({"message": "Invalid Credentials"}), 400  # bad request

    # todo we can handle the error client side to make
    user = Author.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    login_user(user)

    # todo redirect
    return jsonify({"message": "Success"}), 200


@authors_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username", None)
    password = data.get("password", None)

    if username is None or password is None:
        return jsonify({"message": "Invalid Credentials"}), 400  # bad request

    # todo we can handle the error client side to make
    user_exists = Author.query.filter_by(username=username).first()
    if user_exists:
        return jsonify({"message": "User Already exists"}), 409  # username already exists

    user = Author(username=username, password=bcrypt.generate_password_hash(password), host="bigger")
    db.session.add(user)
    db.session.commit()
    login_user(user)

    # todo redirect
    return jsonify({"message": "Success"}), 200
