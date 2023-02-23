from flask import Blueprint, jsonify, request

# note: this blueprint is usually mounted under /authors URL prefix
from flask_login import current_user, login_required

from api import db
from api.user.author.model import Author

followers_bp = Blueprint("followers", __name__)

# resource that i want to read later as to how
# https://stackoverflow.com/questions/19598578/how-do-primaryjoin-and-secondaryjoin-work-for-many-to-many-relationship-in-s


# todo (matt): we need to come up with a format for communicating follow requests in between teams
@followers_bp.route("/<string:author_id>/followers/", methods=["GET"])
def followers(author_id: str):
    """get a list of authors who are AUTHOR_ID’s followers"""
    found_author = Author.query.filter_by(id=author_id).first()
    if not found_author:
        return {"message": "No Author found"}, 404
    return jsonify(found_author.follows.all())


@followers_bp.route("/<string:author_id>/followers/<string:foreign_author_id>", methods=["DELETE"])
def remove_follower(author_id: str, foreign_author_id: str):
    """remove FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID"""
    found_author = Author.query.filter_by(id=author_id).first()
    auth_to_remove = found_author.follows.filter_by(id=foreign_author_id).first()

    if not found_author or not auth_to_remove:
        return {"message": "No Author found"}, 404

    found_author.follows.remove(auth_to_remove)
    db.session.commit()
    return {"message": "Success"}, 200


@followers_bp.route("/<string:author_id>/followers/<string:foreign_author_id>/", methods=["PUT"])
# @login_required
def add_follower(author_id: str, foreign_author_id: str):
    """Add FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID (must be authenticated)"""
    # todo need clarification: does this authentication need an admin? or author_id should be the one authenticated
    followed = Author.query.filter_by(id=author_id).one()
    follower_to_add = Author.query.filter_by(id=foreign_author_id).one()

    if not followed or not follower_to_add:
        return {"message": "No Author found"}, 404

    followed.follows.append(follower_to_add)
    db.session.commit()
    return jsonify({"message": "Success"})


@followers_bp.route("/<string:author_id>/followers/<string:foreign_author_id>/", methods=["GET"])
def check_is_follower(author_id: str, foreign_author_id: str):
    """check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID"""
    followed = Author.query.filter_by(id=author_id).one()
    follower_to_check = Author.query.filter_by(id=foreign_author_id).one()

    if not followed or not follower_to_check:
        return {"message": "No Author found"}, 404

    follower = followed.follows.filter_by(id=foreign_author_id).first()
    if not follower:
        return {"message": "No Author found"}, 404

    return {"message": "Success"}, 200
