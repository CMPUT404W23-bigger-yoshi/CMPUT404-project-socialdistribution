from flask import Blueprint, jsonify, request

# note: this blueprint is usually mounted under /authors URL prefix
from flask_login import current_user, login_required
from flasgger import swag_from
from api import basic_auth, db
from api.user.author.model import Author
from api.user.followers.model import NonLocalFollower, follows_table
from api.user.followers.docs import *

followers_bp = Blueprint("followers", __name__)


@followers_bp.route("/<string:author_id>/followers/", methods=["GET"])
@swag_from(
    {
        "tags": ["Followers"],
        "description": "Return a list of followers of the author with id author_id",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "Author id whose followers are to be returned",
            }
        ],
        "responses": {
            200: {"description": "A list of followers", "schema": followers_schema},
            404: {"description": "Author not found"},
        },
    }
)
@basic_auth.required
def followers(author_id: str):
    """Get a list of authors who are AUTHOR_ID’s followers"""
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    # todo : do we need to ask for more information? unless required will cause response
    #  failure if other teams node throws an error
    non_local_followers = list(found_author.non_local_follows.all())
    local_followers = list(found_author.follows.all())
    local_followers = local_followers + non_local_followers
    return jsonify(local_followers)


@followers_bp.route("/<string:author_id>/followers/count/", methods=["GET"])
@swag_from(
    {
        "tags": ["Followers"],
        "description": "Return the follower count of the author with author_id",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "Author id whose follower count is to be returned",
            }
        ],
        "responses": {
            200: {"description": "Number of followers", "schema": {"properties": {"count": {"type": "integer"}}}},
            404: {"description": "Author not found"},
        },
    }
)
@basic_auth.required
def followers_count(author_id: str):
    """Get the count for the number of poeple following the author"""
    found_author = Author.query.filter_by(id=author_id).first_or_404()

    # todo : do we need to ask for more information? unless required will cause response
    #  failure if other teams node throws an error
    non_local_followers = list(found_author.non_local_follows.all())
    local_followers = list(found_author.follows.all())
    return {"count": len(local_followers) + len(non_local_followers)}, 200


@followers_bp.route("/<string:author_id>/following/count/", methods=["GET"])
@swag_from(
    {
        "tags": ["Followers"],
        "description": "Return the number of people author with author_id follows",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "Author id whose following count is to be returned",
            }
        ],
        "responses": {
            200: {
                "description": "Number of people author is following",
                "schema": {"properties": {"count": {"type": "integer"}}},
            }
        },
    }
)
@basic_auth.required
def following_count(author_id: str):
    """Get the count for the number of people author is following"""
    following = Author.query.filter_by(id=author_id).join(follows_table, follows_table.c.follower_id == Author.id).all()
    non_local_following = NonLocalFollower.query.filter_by(follower_id=author_id).all()
    return {"count": len(following) + len(non_local_following)}, 200


@followers_bp.route("/<string:author_id>/followers/<path:foreign_author_id>", methods=["DELETE"])
@login_required
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
@login_required
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
@swag_from(
    {
        "tags": ["Followers"],
        "description": "Return if foreign author with foreign_author_id is a follower of author with author_id.",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "Author id whose followers are searched for Foreign author.",
            },
            {
                "in": "path",
                "name": "foreign_author_id",
                "type": "string",
                "description": "Id of the foreign author to be checked in author's follower list.",
                "required": "true",
            },
        ],
        "responses": {
            200: {
                "description": "Foreign author is found",
                "schema": {"properties": {"found": {"type": "boolean"}}},
            },
            404: {"description": "Author not found"},
        },
    }
)
@basic_auth.required
def check_is_follower(author_id: str, foreign_author_id: str):
    """Check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID"""
    followed = Author.query.filter_by(id=author_id).first_or_404()
    follower_to_check = Author.query.filter_by(id=foreign_author_id).first()

    if not follower_to_check:
        non_local_follower = NonLocalFollower.query.filter_by(
            followed_id=author_id, follower_id=foreign_author_id
        ).first_or_404()
        return {"found": True}, 200

    follower = followed.follows.filter_by(id=foreign_author_id).first_or_404()

    return {"found": True}, 200
