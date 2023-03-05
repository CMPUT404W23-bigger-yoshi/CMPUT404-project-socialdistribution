from dataclasses import asdict, dataclass

from api.app import db
from api.utils import generate_object_ID, get_author_info


@dataclass
class Comment(db.Model):
    id: int = db.Column(db.String(50), primary_key=True, default="")
    published: str = db.Column("published", db.String(20), nullable=False)
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    comment: str = db.Column("comment", db.String(50), nullable=False)
    # Foreign Key
    author_id: int = db.Column("author_id", db.String(50), nullable=False)
    post_url: int = db.Column("post_url", db.String(50), db.ForeignKey("post.url"), nullable=False)

    def getJSON(self):
        json = asdict(self)
        json["type"] = "comment"

        author = get_author_info(json["author_id"])
        if not author:
            return {}
        json["author"] = author

        del json["author_id"]
        del json["post_url"]

        return json

    def __repr__(self) -> str:
        return f"<Comment {self.id}  author={self.author_id} post={self.post_url}>"
