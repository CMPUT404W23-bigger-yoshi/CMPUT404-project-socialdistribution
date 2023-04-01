from flask_admin.contrib import sqla

from api.admin import RedirectingAuthMixin


class PostView(RedirectingAuthMixin, sqla.ModelView):
    can_view_details = True

    column_list = [
        "url",
        "id",
        "author",
        "published",
        "title",
        "description",
        "contentType",
        "categories",
        "origin",
        "source",
        "visibility",
        "unlisted",
    ]

    column_searchable_list = ["id", "author", "published", "title", "origin"]

    column_default_sort = [("published", True), ("contentType", True)]
