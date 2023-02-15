from datetime import datetime

from api.app import db


class Comment(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    created: datetime = db.Column("created", db.DateTime, nullable=False)
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    content: str = db.Column("content", db.String(50), nullable=False)

    # Foreign Key
    author_id: int = db.Column("author_id", db.Integer, db.ForeignKey("author.id"), nullable=False)
    post_id: int = db.Column("post_id", db.Integer, db.ForeignKey("post.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Comment {self.id}  author={self.author_id} post={self.post_id}>"
