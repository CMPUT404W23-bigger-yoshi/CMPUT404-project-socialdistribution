from dataclasses import dataclass
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

from api import db


@dataclass
class Author(UserMixin, db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    url: str = db.Column("url", db.Text, nullable=True)
    host: str = db.Column("host", db.Text, nullable=False)
    username: str = db.Column("username", db.String(20), nullable=False, unique=True)
    password: str = db.Column("password", db.String(64), nullable=False)
    github: str = db.Column("github", db.Text, nullable=True)
    profile_image: str = db.Column("profile_image", db.Text, default="")


@event.listens_for(Author, "after_insert")
def mymodel_after_insert(mapper, connection, target):
    auth_inserted = Author.__table__
    primary_id = target.id
    statement = auth_inserted.update().where(auth_inserted.c.id == primary_id).values(url=primary_id)
    connection.execute(statement)
