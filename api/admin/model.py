from dataclasses import dataclass

from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, FilterEqual

from api import db


@dataclass
class Connection(db.Model):
    username: str = db.Column(db.Text, primary_key=True)
    password: str = db.Column(db.Text, nullable=False)
    email: str = db.Column(db.String(50), nullable=True)


class AuthAdmin(sqla.ModelView):
    can_view_details = True
    column_list = ["id", "url", "host", "username", "github"]

    column_searchable_list = ["username", "github", "host", "id"]

    column_default_sort = [("username", True)]

    column_filters = ["username", "github", "host"]

    form_create_rules = [
        "username",
        "github",
        "host",
        "password",
    ]

    form_edit_rules = ["username", "github", "host"]
