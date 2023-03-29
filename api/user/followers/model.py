from dataclasses import dataclass

from api import db


class LocalFollower(db.Model):
    follower_url: str = db.Column("follower_url", db.Text, db.ForeignKey("author.url"), primary_key=True)
    followed_url: str = db.Column("followed_url", db.Text, db.ForeignKey("author.url"), primary_key=True)
    approved: bool = db.Column("approved", db.Boolean, nullable=False, default=False)


@dataclass
class NonLocalFollower(db.Model):
    followed_url: str = db.Column(
        "followed_url", db.Text, db.ForeignKey("author.url"), primary_key=True, nullable=False
    )
    follower_url: str = db.Column("follower_url", db.Text, primary_key=True)
    approved: bool = db.Column("approved", db.Boolean, nullable=False, default=False)
