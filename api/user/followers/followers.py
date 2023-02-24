from flask import Blueprint, jsonify, request

# note: this blueprint is usually mounted under /authors URL prefix
from flask_login import current_user, login_required

from api import db
from api.user.author.model import Author
from api.user.followers.model import NonLocalFollower

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
    # todo : do we need to ask for more information? unless required will cause response
    #  failure if other teams node throws an error
    non_local_followers = list(found_author.non_local_follows.all())
    local_followers = list(found_author.follows.all())
    local_followers = local_followers + non_local_followers
    return jsonify(local_followers)


@followers_bp.route("/<string:author_id>/followers/<path:foreign_author_id>", methods=["DELETE"])
def remove_follower(author_id: str, foreign_author_id: str):
    """remove FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID"""
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    auth_to_remove = found_author.follows.filter_by(id=foreign_author_id).first()

    # local author doesn't exist
    if not auth_to_remove:
        non_local_follower = NonLocalFollower.query.filter_by(
            follower_id=foreign_author_id, followed_id=author_id
        ).first_or_404()
        db.session.delete(non_local_follower)
        db.session.commit()
        return {"message": "Success"}, 200

    found_author.follows.remove(auth_to_remove)
    db.session.commit()
    return {"message": "Success"}, 200


@followers_bp.route("/<string:author_id>/followers/<path:foreign_author_id>/", methods=["PUT"])
# @login_required
def add_follower(author_id: str, foreign_author_id: str):
    """Add FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID (must be authenticated)"""
    # todo need clarification: does this authentication need an admin? or author_id should be the one authenticated
    followed = Author.query.filter_by(id=author_id).first()
    follower_to_add = Author.query.filter_by(id=foreign_author_id).first()

    if not followed:
        return {"message": "No Author found"}, 404

    if not follower_to_add:
        follower_to_add = NonLocalFollower(followed_id=followed.id, follower_id=foreign_author_id)
        followed.non_local_follows.append(follower_to_add)
        db.session.add(follower_to_add)
        db.session.commit()
        return {"message": "Success"}

    followed.follows.append(follower_to_add)
    db.session.commit()
    return jsonify({"message": "Success"})


@followers_bp.route("/<string:author_id>/followers/<path:foreign_author_id>/", methods=["GET"])
def check_is_follower(author_id: str, foreign_author_id: str):
    """check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID"""
    followed = Author.query.filter_by(id=author_id).first_or_404()
    follower_to_check = Author.query.filter_by(id=foreign_author_id).first()

    if not follower_to_check:
        non_local_follower = NonLocalFollower.query.filter_by(
            followed_id=author_id, follower_id=foreign_author_id
        ).first_or_404()
        return {"message": "Success"}, 200

    follower = followed.follows.filter_by(id=foreign_author_id).first_or_404()

    return {"message": "Success"}, 200
