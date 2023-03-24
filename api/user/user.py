from flask import Blueprint

from api.user.author.authors import authors_bp
from api.user.comments import comments_bp
from api.user.followers.followers import followers_bp
from api.user.posts.posts import posts_bp

user_bp = Blueprint("users", __name__)
user_bp.register_blueprint(authors_bp)
user_bp.register_blueprint(followers_bp)
user_bp.register_blueprint(posts_bp)
user_bp.register_blueprint(comments_bp)
