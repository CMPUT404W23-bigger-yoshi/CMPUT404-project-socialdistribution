from flask import Blueprint

from api.utils import get_pagination_params

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/<string:author_id>/posts/<string:post_id>/comments", methods=["GET"])
def get_comments(author_id: str, post_id: str):
    """get the list of comments of the post whose id is POST_ID (paginated)"""
    pagination = get_pagination_params()
    return {"comments": ["", ""]}


@comments_bp.route("/<string:author_id>/posts/<string:post_id>/comments", methods=["POST"])
def post_comment(author_id: str, post_id: str):
    """if you post an object of “type”:”comment”, it will add your comment to the post whose id is POST_ID"""
    pass
