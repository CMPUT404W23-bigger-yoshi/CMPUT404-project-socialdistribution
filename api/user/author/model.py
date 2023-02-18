from datetime import datetime
from api.user.relations import author_likes_comments, author_likes_posts
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from dataclasses import dataclass, asdict
from api import db
from api.utils import generate_object_ID

@dataclass
class Author(db.Model):
    id: str = db.Column(db.String(50), primary_key=True, default=generate_object_ID())
    url: str = db.Column("url", db.Text, nullable=True)
    host: str = db.Column("host", db.Text, nullable=False)
    displayName: str = db.Column("displayName", db.String(20), nullable=False)
    github: str = db.Column("github", db.Text, nullable=False)
    profileImage: str = db.Column("profileImage", db.Text, default="")
    # Relationships
    posts_liked = db.relationship("Post", secondary=author_likes_posts, backref='authors')
    comments_liked = db.relationship("Comment", secondary=author_likes_comments, backref='authors')
    object_id:str = db.Column(db.String(50), unique=True, nullable=True)

    def getJSON(self) -> dict:
        json = asdict(self)
        json['type'] = 'author'
        del json['object_id']

        return json

@event.listens_for(Author, "after_insert")
def mymodel_after_insert(mapper, connection, target):
    auth_inserted = Author.__table__
    primary_id = target.id
    host = target.host

    # Need this for correct url 
    if not host.endswith('/'):
        host += '/'

    complete_url = host + 'authors/' + primary_id
    change_url = auth_inserted.update().where(auth_inserted.c.id == primary_id).values(url=complete_url, id=complete_url, object_id=primary_id)
    connection.execute(change_url)
