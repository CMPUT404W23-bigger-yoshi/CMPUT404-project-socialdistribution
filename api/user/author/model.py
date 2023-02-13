from dataclasses import dataclass
from datetime import datetime
from api.user.relations import author_likes_comments, author_likes_posts
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

from api import db


@dataclass
class Author(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    url: str = db.Column("url", db.Text, nullable=True)
    host: str = db.Column("host", db.Text, nullable=False)
    displayName: str = db.Column("displayName", db.String(20), nullable=False)
    github: str = db.Column("github", db.Text, nullable=False)
    profileImage: str = db.Column("profileImage", db.Text, default="")

    # Relationships
    posts_liked = db.relationship("Post", secondary=author_likes_posts, backref='authors')
    comments_liked = db.relationship("Comment", secondary=author_likes_comments, backref='authors')


@event.listens_for(Author, "after_insert")
def mymodel_after_insert(mapper, connection, target):
    auth_inserted = Author.__table__
    primary_id = target.id
    statement = auth_inserted.update().where(auth_inserted.c.id == primary_id).values(url=primary_id)
    connection.execute(statement)
