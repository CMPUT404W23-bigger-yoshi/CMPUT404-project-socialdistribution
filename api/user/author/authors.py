from flask import Blueprint, jsonify, request

from api import db
from api.user.author.model import Author
from api.utils import get_pagination_params

# note: this blueprint is usually mounted under /authors URL prefix
authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/", methods=["GET"])
def get_authors():
    authors = Author.query.all()
    return jsonify(authors)


@authors_bp.route("/admin", methods=["POST"])
def create_author():
    data = request.json
    displayName = data.get("displayName", None)
    github = data.get("github", None)
    host = data.get("host", None)
    profileImage = data.get("profileImage", None)

    author_to_add = Author(displayName=displayName, github=github, host=host, profileImage=profileImage)
    db.session.add(author_to_add)
    db.session.commit()
    return {"Success": 1}


@authors_bp.route("/<string:author_id>", methods=["GET"])
def get_single_author(author_id: str):
    return {"author": author_id}
