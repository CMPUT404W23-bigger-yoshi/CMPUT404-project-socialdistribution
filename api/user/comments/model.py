from dataclasses import asdict, dataclass

from api import db
from api.utils import generate_object_ID


@dataclass
class Comment(db.Model):
    id: str = db.Column(db.String(50), primary_key=True, default="")
    created: str = db.Column("created", db.String(20), nullable=False)
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    content: str = db.Column("content", db.String(50), nullable=False)
    # we can't enforce an FK constraint here - we may be commenting on a remote post
    author_id: str = db.Column("author_id", db.String(200), nullable=False)
    post_id: str = db.Column("post_id", db.String(200), db.ForeignKey("post.id"), nullable=False)

    def getJSON(self):
        json = asdict(self)

    def __repr__(self) -> str:
        return f"<Comment {self.id}  author={self.author_id} post={self.post_id}>"
