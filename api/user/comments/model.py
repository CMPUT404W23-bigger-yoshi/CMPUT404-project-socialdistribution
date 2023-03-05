from dataclasses import asdict, dataclass

from api.app import db
from api.utils import generate_object_ID, get_author_info


@dataclass
class Comment(db.Model):
    id: str = db.Column(db.String(50), primary_key=True, default=generate_object_ID)
    published: str = db.Column("published", db.String(20), nullable=False)
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    comment: str = db.Column("comment", db.String(50), nullable=False)
    # Foreign Key
    author_id: str = db.Column("author_id", db.String(50), nullable=False)
    post_id: str = db.Column("post_id", db.String(50), db.ForeignKey("post.id"), nullable=False)

    def getJSON(self):
        json = asdict(self)
        json["type"] = "comment"

        author = get_author_info(json["author_id"])
        if not author:
            return {}
        json["author"] = author
        json["id"] = self.post.url + "/comments/" + self.id

        del json["author_id"]
        del json["post_id"]

        return json

    def __repr__(self) -> str:
        return f"<Comment {self.id}  author={self.author_id} post={self.post_id}>"
