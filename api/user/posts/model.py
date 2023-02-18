import enum
from datetime import datetime

from sqlalchemy import Enum

from api.app import db


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


class Post(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    published: datetime = db.Column("published", db.DateTime, nullable=False)  # is datetime a valid way?
    title: str = db.Column("title", db.String(120), nullable=False)
    origin: str = db.Column("origin", db.Text, nullable=False)
    source: str = db.Column("source", db.Text, nullable=False)
    description: str = db.Column("short_desc", db.String(100))
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    content: str = db.Column("content", db.Text, nullable=False)

    # categories will be comma separated values
    categories: str = db.Column("categories", db.Text)

    # 0 -> "PUBLIC", 1-> "FRIENDS"
    visibility: Visibility = db.Column("visibility", Enum(Visibility), nullable=False, default=Visibility.PUBLIC)

    unlisted: bool = db.Column("unlisted", db.Boolean, nullable=False, default=False)

    # Foreign Key
    author_id: int = db.Column("author_id", db.Integer, db.ForeignKey("author.id"), nullable=False)

<<<<<<< HEAD
    # Post.comments -> comments.Comment
    comments = db.relationship("Comment", backref="post", lazy="dynamic")
=======
    # Relationships -> lazy = "dynamic" returns a query object to further refine. 
    comments = db.relationship("Comment", backref="post", lazy="dynamic")  # what will be the type of this?
>>>>>>> c275a5d8 (Added relationships)

    def __repr__(self) -> str:
        return f"<Post {self.id} author={self.author_id} title={self.title}>"
