from dataclasses import asdict, dataclass

from flask import jsonify
from sqlalchemy import Enum, event

from api import db
from api.user.author.model import Author, NonLocalAuthor
from api.utils import Visibility, generate_object_ID, get_pagination_params


def _constructURL(context):
    id = context.get_current_parameters()["id"]
    author_url = context.get_current_parameters()["author"]
    url = author_url + "/posts/" + id
    return url


inbox_table = db.Table(
    "inbox",
    db.Column("post_id", db.String(200), db.ForeignKey("post.id", ondelete="CASCADE"), primary_key=True),
    db.Column("meant_for", db.String(200), db.ForeignKey("author.id", ondelete="CASCADE"), primary_key=True),
)


@dataclass
class Post(db.Model):
    id: str = db.Column(db.String(50), nullable=True, default=generate_object_ID, unique=True, primary_key=True)
    url: str = db.Column(db.Text, default=_constructURL)
    published: str = db.Column("published", db.String(50), nullable=False)
    title: str = db.Column("title", db.Text, nullable=False)
    origin: str = db.Column("origin", db.Text, nullable=False)
    # server -> the last server from which this post was sent into the inbox of the receiver
    source: str = db.Column("source", db.Text, nullable=False)
    description: str = db.Column("shortDesc", db.String(100))
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    content: str = db.Column("content", db.Text, nullable=False)
    # categories will be comma separated values
    categories: str = db.Column("categories", db.Text)

    # 0 -> "PUBLIC", 1-> "FRIENDS"
    visibility: Visibility = db.Column("visibility", Enum(Visibility), nullable=False, default=Visibility.PUBLIC)

    # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in
    # timelines
    unlisted: bool = db.Column("unlisted", db.Boolean, nullable=False, default=False)

    author: str = db.Column("author", db.String(50), nullable=False)

    # Relationships -> lazy = "dynamic" returns a query object to further refine.
    # comments = db.relationship(
    #     "Comment", backref="post", lazy="dynamic", cascade="all, delete"
    # )  # what will be the type of this?

    # TODO Images

    def getJSON(self) -> dict:
        post = asdict(self)
        post["type"] = "post"

        # Setting author
        author = Author.query.filter_by(id=post["author"]).first()
        if author:
            post["author"] = author.getJSON()

        if author is None:
            author = NonLocalAuthor.query.filter_by(id=post["author"]).first()
            if author:
                # todo @matt is there a better way?
                # todo future: fetch latest data, if not available return stale data
                author = {**author.__dict__}
                if author.get("_sa_instance_state", None) is not None:
                    del author["_sa_instance_state"]
                post["author"] = author

        # Categories
        if post["categories"]:
            post["categories"] = post["categories"].split(",")

        # Visibility
        if post["visibility"] == Visibility.PUBLIC:
            post["visibility"] = "PUBLIC"
        elif post["visibility"] == Visibility.FRIENDS:
            post["visibility"] = "FRIENDS"

        # Comments
        post_id = post["id"]
        curr_post = Post.query.filter_by(id=post_id).first()
        # comments = list(curr_post.comments.all())

        # comments = [comment.getJSON() for comment in comments]

        # Renaming url to id
        post["id"] = post["url"]
        # post["comments"] = comments
        del post["url"]
        return post

    def __repr__(self) -> str:
        return f"<Post {self.id} author={self.author} title={self.title}>"
