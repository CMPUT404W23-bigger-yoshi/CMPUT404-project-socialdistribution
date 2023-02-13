from flask import Blueprint, jsonify, request

from api import db
from api.user.author.model import Author
from api.utils import get_pagination_params

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
    paginator = get_pagination_params()
    authors = Author.query.paginate(page=1, per_page=paginator.size).items
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
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    return jsonify(found_author)
