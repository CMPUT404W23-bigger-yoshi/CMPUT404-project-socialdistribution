import base64
from dataclasses import dataclass

from flask import flash
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext
from flask_admin.contrib import sqla

from api import db
from api.admin import RedirectingAuthMixin
from api.utils import Approval


@dataclass
class OutboundConnection(db.Model):
    endpoint: str = db.Column(db.Text, primary_key=True)
    username: str = db.Column(db.Text, nullable=False)
    password: str = db.Column(db.Text, nullable=False)

    @property
    def auth_header_dict(self):
        """returns the auth header for a given Connection instance"""
        if None in (self.password, self.username):
            raise ValueError(f"REFUSING TO GENERATE CREDENTIALS because user/pass is None!")
        # encoded the string in bytes, b64encode those bytes, then decode those bytes to str
        return {"Authorization": f"Basic " + base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}

    def matches_url(self, url: str):
        return url.startswith(self.endpoint)


class OutboundConnectionView(RedirectingAuthMixin, sqla.ModelView):
    can_view_details = True

    column_list = ["username", "password", "endpoint"]

    column_searchable_list = ["username", "endpoint"]

    column_editable_list = column_list

    column_default_sort = [("endpoint", True)]

    column_filters = column_list

    form_columns = column_list

    form_create_rules = column_list

    form_edit_rules = column_list
