from dataclasses import dataclass

from api import db


class LocalFollower(db.Model):
    follower_url: str = db.Column("follower_url", db.Text, db.ForeignKey("author.url"), primary_key=True)
    followed_url: str = db.Column("followed_url", db.Text, db.ForeignKey("author.url"), primary_key=True)
    approved: bool = db.Column("approved", db.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return (
            f"<LocalFollower follower: {self.followed_url}, followed: {self.followed_url}, approved: {self.approved}>"
        )


@dataclass
class NonLocalFollower(db.Model):
    followed_url: str = db.Column(
        "followed_url", db.Text, db.ForeignKey("author.url"), primary_key=True, nullable=False
    )
    follower_url: str = db.Column("follower_url", db.Text, primary_key=True)
    approved: bool = db.Column("approved", db.Boolean, nullable=False, default=False)
