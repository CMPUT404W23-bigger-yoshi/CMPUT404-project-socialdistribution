import base64
import logging
import os
from json import JSONDecodeError
from typing import List

import requests
from flasgger import swag_from
from flask import Blueprint, request
from flask_login import current_user, login_required, login_user, logout_user

from api import basic_auth, bcrypt, db
from api.admin.outbound_connection import OutboundConnection
from api.admin.utils import auth_header_for_url
from api.user.author.docs import author_schema, authors_schema
from api.user.author.model import Author
from api.utils import Approval, Role, cache_request, get_pagination_params

logger = logging.getLogger(__name__)

# note: this blueprint is usually mounted under /authors URL prefix
authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/", methods=["GET"])
@swag_from(
    {
        "tags": ["Authors"],
        "description": "Returns list of authors",
        "parameters": [
            {
                "in": "query",
                "name": "page",
                "description": "Page number of the resulting authors list",
                "type": "integer",
            },
            {"in": "query", "name": "size", "description": "Number of items per page", "type": "integer"},
        ],
        "responses": {200: {"description": "A List of authors", "schema": authors_schema}},
    }
)
@basic_auth.required
def get_authors():
    """Get a list of all authors registered with Bigger Yoshi"""
    authors = Author.query.paginate(**get_pagination_params().dict).items
    items = [author.getJSON() for author in authors]
    authors_json = {"type": "authors", "items": items}

    return authors_json


@authors_bp.route("/<string:author_id>", methods=["GET"])
@swag_from(
    {
        "tags": ["Authors"],
        "description": "Returns an Author with id",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "The id of author to retrieve",
            }
        ],
        "responses": {
            200: {"description": "Returns a single author", "schema": author_schema},
            404: {"desciption": "Author not found"},
        },
    }
)
@basic_auth.required
def get_single_author(author_id: str):
    """Get the author with id author_id"""
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    return found_author.getJSON()


@authors_bp.route("/<string:author_id>", methods=["POST"])
@login_required
def update_author(author_id: str):
    # Logged in author can only update their own profile
    if current_user.id != author_id:
        return {"message": "Unauthorized"}, 401

    found_author = Author.query.filter_by(id=author_id).first_or_404()
    data = request.json
    displayName = data.get("displayName", None)
    github = data.get("github", None)
    host = data.get("host", None)
    profileImage = data.get("profileImage", None)

    if displayName:
        exists = Author.query.filter(Author.username == displayName, Author.id != author_id).first()
        if exists:
            return {"message": "Username already exists. Try some other name"}, 409
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

    # todo (matt): figure out what the below comment means
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

    user = Author(
        username=username,
        password=bcrypt.generate_password_hash(password).decode("utf-8"),
        host=request.host,
        approval=Approval.PENDING,
        role=Role.USER,
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return {"message": "Success"}, 200


@authors_bp.route("/create-admin/", methods=["POST"])
def create_admin():
    data = request.json
    secret = data.get("secret-admin")
    if secret != os.environ.get("SECRET_ADMIN"):
        return {"Not permitted"}, 401

    username = data.get("username")
    password = data.get("password")

    if username is None or password is None:
        return {"Missing fields"}, 400

    user_exists = Author.query.filter_by(username=username).first()
    if user_exists:
        return {"message": "User Already exists"}, 409

    user = Author(
        username=username,
        password=bcrypt.generate_password_hash(password).decode("utf-8"),
        host=request.host,
        approval=Approval.APPROVED,
        role=Role.ADMIN,
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return {"message": "Success"}, 201


@authors_bp.route("/foreign/<path:url>", methods=["GET"])
def get_foreign_author(url: str):
    r = requests.get(url)
    data = r.json()
    return data


@authors_bp.route("/<string:author_username>/search/multiple", methods=["GET"])
def get_author_id_all(author_username: str):
    local_authors = Author.query.filter(
        Author.username.like(f"%{author_username}%"), Author.id != current_user.id
    ).all()

    items = [author.getJSON() for author in local_authors]
    # this endpoint gets hammered - once per keystroke. good thing there's only a few authors per server :shrug:
    all_connections: List[OutboundConnection] = OutboundConnection.query.all()
    logger.info(f"querying {len(all_connections)=} endpoints for authors")
    # yes, it is sequential (for now)
    # I do not care
    for con in all_connections:
        authors_url = con.endpoint + "authors/"
        logger.debug(f"making request for authors: {authors_url=} headers={auth_header_for_url(authors_url)}")
        r = None
        try:
            # nobody will have more than 100 authors, so we don't bother to write the code to query more than that
            r = cache_request.get(authors_url, headers=auth_header_for_url(authors_url), params={"size": 100})
            items.extend(r.json().get("items", []))
        except JSONDecodeError:
            logger.error(f"failed to parse JSON response {r.status_code=} {r.content.decode()=}")
        except Exception as e:
            logger.exception(f"failed to make request to {authors_url=}: ")

    return {"type": "authors", "items": items}
