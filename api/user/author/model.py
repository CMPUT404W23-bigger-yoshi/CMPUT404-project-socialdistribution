from dataclasses import dataclass
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from api.app import db


@dataclass
class Author(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    url: str = db.Column("url", db.Text, nullalbe=False)
    host: str = db.Column("host", db.Text, nullalbe=False)
    displayName: str = db.Column("displayName", db.String(20), nullable=False)
    github: str = db.Column("github", db.Text, nullable=False)
    profileImage: str = db.Column("profileImage", db.Text, default="")

    def __repr__(self) -> str:
        representation = (
            ""
            + "<< Comment: {}\n"
            + "   Post-id: {}\n"
            + "   Created on: {}\n"
            + "   Content-Type: {}\n"
            + "   Content: {} >>\n"
        ).format(self.id, self._post_id, self._created, self._contentType, self._content)

        return representation
