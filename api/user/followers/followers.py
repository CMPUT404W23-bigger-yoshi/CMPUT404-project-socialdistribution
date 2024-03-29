from flasgger import swag_from
from flask import Blueprint, jsonify, request

# note: this blueprint is usually mounted under /authors URL prefix
from flask_login import current_user, login_required
from sqlalchemy import and_

from api import basic_auth, db
from api.user.author.model import Author, NonLocalAuthor
from api.user.followers.docs import *
from api.user.followers.model import LocalFollower, NonLocalFollower

followers_bp = Blueprint("followers", __name__)


@followers_bp.route("/<string:author_id>/followers", methods=["GET"])
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
    """Get a list of authors who are author_id’s followers"""
    found_author = Author.query.filter_by(id=author_id).first_or_404()

    local_followers = (
        Author.query.join(LocalFollower, Author.url == LocalFollower.follower_url)
        .filter_by(approved=True, followed_url=found_author.url)
        .all()
    )
    non_local_followers = (
        NonLocalAuthor.query.join(NonLocalFollower, NonLocalAuthor.url == NonLocalFollower.follower_url)
        .filter_by(approved=True, followed_url=found_author.url)
        .all()
    )
    return {"type": "followers", "items": [author.getJSON() for author in local_followers + non_local_followers]}


@followers_bp.route("/<string:author_id>/followers/count", methods=["GET"])
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
    following = LocalFollower.query.filter_by(followed_url=found_author.url, approved=True).count()
    non_local_following = NonLocalFollower.query.filter_by(followed_url=found_author.url, approved=True).count()

    return {"count": following + non_local_following}


@followers_bp.route("/<string:author_id>/followers/<path:follower_url>", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Followers"],
        "description": "Remove follower with follower_url from the followers list of author with author_id",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "The ID of the author whose followers list the follower is being removed from",
            },
            {
                "in": "path",
                "name": "follower_url",
                "type": "string",
                "required": "true",
                "description": "The URL of the follower being removed",
            },
        ],
        "responses": {
            200: {"description": "Success"},
            404: {"description": "Either author or follower not found"},
        },
    }
)
@login_required
def remove_follower(author_id: str, follower_url: str):
    """Remove follower with follower_url from the followers list of author with author_id"""
    found_author = Author.query.filter_by(id=author_id).first_or_404()
    print(found_author)
    islocal = LocalFollower.query.filter_by(followed_url=found_author.url, follower_url=follower_url).first()
    print(islocal)
    # local author doesn't exist
    if not islocal:
        non_local_follower = NonLocalFollower.query.filter_by(
            follower_url=follower_url, followed_url=found_author.url
        ).first_or_404()
        db.session.delete(non_local_follower)
        db.session.commit()
        return {"message": "Success"}, 200

    db.session.delete(islocal)
    db.session.commit()
    return {"message": "Success"}, 200


@followers_bp.route("/<string:followed_id>/followers/<path:follower_id>", methods=["PUT"])
@swag_from(
    {
        "tags": ["Followers"],
        "description": "Add a follower to a given author",
        "parameters": [
            {
                "in": "path",
                "name": "followed_id",
                "type": "string",
                "required": "true",
                "description": "The ID of the author to whom a follower is being added",
            },
            {
                "in": "path",
                "name": "follower_id",
                "type": "string",
                "required": "true",
                "description": "The ID of the follower being added",
            },
        ],
        "responses": {
            200: {"description": "Approved local follower!"},
            400: {"description": "The follower is already approved"},
            404: {"description": "follower already approved or failed to approve existing follow request"},
        },
    }
)
@login_required
def add_follower(followed_id: str, follower_id: str):
    """
    Add follower_id (local or remote) as a follower of followed_id (local) as a follower of author_id
    """
    # I don't care we're fetching more than we need to here
    followed_author = Author.query.filter_by(id=followed_id).first_or_404()
    foreign_follow = NonLocalFollower.query.filter_by(
        followed_url=followed_author.url, follower_url=follower_id
    ).first()
    local_follow = LocalFollower.query.filter_by(followed_url=followed_author.url, follower_url=follower_id).first()

    for follow_state in [foreign_follow, local_follow]:
        # assume no collision between these 2 tables, ie, if one record is found in one table to be approved,
        # we can confidently give a 400 error that this user is already approved
        if follow_state:
            if follow_state.approved:
                return {"success": 0, "message": "follower already approved"}, 400
            else:
                follow_state.approved = True
                db.session.commit()
                return {"success": 0, "message": "Approved local follower!"}, 200
    # neither a foreign, nor local follow was found to be pending, so there's nothing to approve here
    return {"success": 0, "message": "failed to approve existing follow request"}, 400


@followers_bp.route("/<string:author_id>/followers/<path:follower_url>", methods=["GET"])
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
def check_is_follower(author_id: str, follower_url: str):
    """Check if foreign_author_id is a follower of author_id"""
    followed = Author.query.filter_by(id=author_id).first_or_404()
    islocal = LocalFollower.query.filter_by(followed_url=followed.url, follower_url=follower_url).first()
    found = True
    if not islocal:
        non_local_follower = NonLocalFollower.query.filter_by(
            followed_url=followed.url, follower_url=follower_url
        ).first()
        if not non_local_follower:
            found = False
        return {"found": found}, 200
    return {"found": found}, 200


@followers_bp.route("/<string:author_id>/follow-requests", methods=["GET"])
def get_follow_notification(author_id: str):
    author = Author.query.filter_by(id=author_id).first_or_404()
    local_followers = (
        Author.query.join(LocalFollower, Author.url == LocalFollower.follower_url)
        .filter_by(approved=False, followed_url=author.url)
        .all()
    )
    non_local_followers = (
        NonLocalAuthor.query.join(NonLocalFollower, NonLocalAuthor.url == NonLocalFollower.follower_url)
        .filter_by(approved=False, followed_url=author.url)
        .all()
    )
    res = [{"author": {**follower.getJSON()}, "type": "follow"} for follower in local_followers + non_local_followers]
    return {"message": "Success", "follow_requests": res}
