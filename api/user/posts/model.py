from dataclasses import asdict, dataclass

from sqlalchemy import Enum, event

from api import db
from api.user.author.model import Author
from api.utils import Visibility, generate_object_ID, get_pagination_params


def _constructURL(context):
    id = context.get_current_parameters()["id"]
    author_url = context.get_current_parameters()["author"]
    url = author_url + "/posts/" + id
    return url


@dataclass
class Post(db.Model):
    id: str = db.Column(db.String(50), nullable=True, default=generate_object_ID, unique=True, primary_key=True)
    url: str = db.Column(db.Text, default=_constructURL)
    published: str = db.Column("published", db.String(20), nullable=False)
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

    # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
    unlisted: bool = db.Column("unlisted", db.Boolean, nullable=False, default=False)

    # Foreign Key - Recipient must be a local author
    inbox: str = db.Column("inbox", db.String(50), db.ForeignKey("author.id"), primary_key=True, nullable=False)

    # Complete URL of the author remote/local -> cant be a foreign key
    author: str = db.Column("author", db.String(50), nullable=False)

    # Relationships -> lazy = "dynamic" returns a query object to further refine.
    comments = db.relationship(
        "Comment", backref="post", lazy="dynamic", cascade="all, delete"
    )  # what will be the type of this?

    # TODO Images

    def getJSON(self) -> dict:
        post = asdict(self)
        post["type"] = "post"

        # Setting author
        author = Author.query.filter_by(url=post["author"]).first()
        post["author"] = author.getJSON()

        # Categories
        if post["categories"]:
            post["categories"] = post["categories"].split(",")

        # Visibility
        if post["visibility"] == Visibility.PUBLIC:
            post["visibility"] = "PUBLIC"
        elif post["visibility"] == Visibility.FRIENDS:
            post["visibility"] = "FRIENDS"

        # Comments
        # post["count"] = len(self.comments.all())
        # comments_url = post["url"] + "/comments"
        # post["comments"] = comments_url
        #
        # commentSrc = {
        #     "id": comments_url,
        #     "type": "comments",
        #     "page": get_pagination_params().page,
        #     "size": get_pagination_params().size,
        #     "post": post["url"],
        # }

        # Renaming url to id
        post["id"] = post["url"]

        # TODO jsonify comments correctly here
        # commentSrc["comments"] = self.comments.paginate(**get_pagination_params().as_dict()).items
        #
        # post["commentSrc"] = commentSrc
        del post["inbox"]
        del post["url"]
        return post

    def __repr__(self) -> str:
        return f"<Post {self.id} author={self.author} title={self.title}>"
