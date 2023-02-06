from flask import Blueprint
from .authors import authors_bp
from .followers import followers_bp
from .posts import posts_bp

user_bp = Blueprint("users", __name__)
user_bp.register_blueprint(authors_bp)
user_bp.register_blueprint(followers_bp)
user_bp.register_blueprint(posts_bp)
