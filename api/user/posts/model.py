import enum
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Enum

from api.app import db


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


@dataclass
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
    visibility: Visibility = db.Column("visibility", Enum(Visibility), nullable=False)

    unlisted: bool = db.Column("unlisted", db.Boolean, nullable=False)

    # Foreign Key
    author_id: int = db.Column("author_id", db.Integer, db.ForeignKey("author.id"), nullable=False)

    # Post.comments -> comments.Comment
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Post {self.id} title={self.title} author={self.author_id}>"
