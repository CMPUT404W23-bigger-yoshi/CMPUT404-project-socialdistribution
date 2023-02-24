from dataclasses import dataclass

from api import db

follows_table = db.Table(
    "follows",
    db.Column("follower_id", db.Integer, db.ForeignKey("author.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("author.id"), primary_key=True),
)


@dataclass
class NonLocalFollower(db.Model):
    followed_id: str = db.Column(
        "followed_id", db.Integer, db.ForeignKey("author.id"), primary_key=True, nullable=False
    )
    follower_id: str = db.Column("follower_id", db.String(50), primary_key=True)
