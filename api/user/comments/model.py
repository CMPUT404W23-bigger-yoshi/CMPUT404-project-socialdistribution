from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from api.app import db


class Comment(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    _created = db.Column("created", db.DateTime, nullable=False)
    _contentType = db.Column("contentType", db.String(50), nullable=False)
    _content = db.Column("content", db.String(50), nullable=False)

    # Foreign Key
    _post_id = db.Column("post_id", db.Integer, db.ForeignKey("post.id"), nullable=False)

    def __init__(self, created: datetime, contentType: str, content: str, post_id: int):
        self._content = content
        self._contentType = contentType
        self._created = created
        self._post_id = post_id

    def __repr__(self) -> str:
        repr = (
            ""
            + "<< Comment: {}\n"
            + "   Post-id: {}\n"
            + "   Created on: {}\n"
            + "   Content-Type: {}\n"
            + "   Content: {} >>\n"
        ).format(self._id, self._post_id, self._created, self._contentType, self._content)

        return repr
