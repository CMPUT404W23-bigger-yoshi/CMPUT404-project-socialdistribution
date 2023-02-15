from flask import Blueprint, jsonify, request

from api import db
from api.user.author.model import Author
from api.utils import get_pagination_params, password_hash

# note: this blueprint is usually mounted under /authors URL prefix
authors_bp = Blueprint("authors", __name__)


# todo: how to interpret it?
# URL: ://service/authors/
#
#     GET [local, remote]: retrieve all profiles on the server (paginated)
#         page: how many pages
#         size: how big is a page
#
# Example query: GET ://service/authors?page=10&size=5
#
#     Gets the 5 authors, authors 45 to 49.


@authors_bp.route("/", methods=["GET"])
def get_authors():
    args = request.args
    authors = Author.query.paginate(**get_pagination_params().as_dict).items
    return jsonify(authors)


@authors_bp.route("/admin", methods=["POST"])
def create_author():
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


@authors_bp.route("/register", methods=["POST"])
def register_user():
    p = request.json
    # todo: not sure why I don't have username here :)

    username = "testuser101"  # p["username"]
    if p["password"] != p["confirmPassword"]:
        # todo: return error back to backend here
        raise ValueError("fix me")

    user_exists = Author.query.filter_by(username=username).first()
    if user_exists:
        # todo: return user exist
        raise ValueError("fix me")

    to_insert = Author(username=username, password=password_hash(p["password"]))
    db.session.add(to_insert)
    db.session.commit()
    breakpoint()
