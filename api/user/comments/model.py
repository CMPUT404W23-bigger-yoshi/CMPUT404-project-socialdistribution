from dataclasses import asdict, dataclass

from api import db
from api.user.author.model import Author, NonLocalAuthor
from api.utils import generate_object_ID, get_author_info


@dataclass
class Comment(db.Model):
    id: str = db.Column(db.Text, primary_key=True, default=generate_object_ID)
    published: str = db.Column("published", db.Text, nullable=False)
    contentType: str = db.Column("contentType", db.Text, nullable=False)
    comment: str = db.Column("comment", db.Text, nullable=False)
    # we can't enforce an FK constraint here - we may be commenting on a remote post
    author_id: str = db.Column("author_id", db.Text, nullable=False)
    post_id: str = db.Column("post_id", db.Text, db.ForeignKey("post.id"), nullable=False)

    def getJSON(self):
        json = asdict(self)
        json["type"] = "comment"

        # todo write a better way
        author_id = json["author_id"]
        author = Author.query.filter_by(id=author_id).first()
        if author is None:
            author = NonLocalAuthor.query.filter_by(id=author_id).first()

        author = author.getJSON() if author is not None else {}

        json["author"] = author
        json["id"] = self.post.url + "/comments/" + self.id

        del json["author_id"]
        del json["post_id"]

        return json

    def __repr__(self) -> str:
        return f"<Comment {self.id}  author={self.author_id} post={self.post_id}>"
