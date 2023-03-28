from dataclasses import dataclass

from api import db


class LocalFollower(db.Model):
    follower_id: str = db.Column("follower_id", db.Text, db.ForeignKey("author.id"), primary_key=True)
    followed_id: str = db.Column("followed_id", db.Text, db.ForeignKey("author.id"), primary_key=True)
    approved: bool = db.Column("approved", db.Boolean, nullable=False, default=False)


@dataclass
class NonLocalFollower(db.Model):
    followed_id: str = db.Column("followed_id", db.Text, db.ForeignKey("author.id"), primary_key=True, nullable=False)
    follower_id: str = db.Column("follower_id", db.Text, primary_key=True)
    approved: bool = db.Column("approved", db.Boolean, nullable=False, default=False)
