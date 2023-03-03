from dataclasses import asdict, dataclass

from api.app import db
from api.utils import generate_object_ID


@dataclass
class Comment(db.Model):
    id: int = db.Column(db.String(50), primary_key=True, default="")
    created: str = db.Column("created", db.String(20), nullable=False)
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    content: str = db.Column("content", db.String(50), nullable=False)
    # Foreign Key
    author_id: int = db.Column("author_id", db.Integer, nullable=False)
    post_url: int = db.Column("post_url", db.Integer, db.ForeignKey("post.url"), nullable=False)

    def getJSON(self):
        json = asdict(self)

    def __repr__(self) -> str:
        return f"<Comment {self.id}  author={self.author_id} post={self.post_url}>"
