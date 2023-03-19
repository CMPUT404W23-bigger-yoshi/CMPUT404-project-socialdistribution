from dataclasses import dataclass

from flask import flash
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, FilterEqual
from sqlalchemy import Enum

from api import db
from api.admin.APIConfig import APIConfig
from api.user.author.model import Author
from api.utils import Approval


def _default_approval_from_config(context):
    if APIConfig.connection_approval:
        return Approval.APPROVED
    else:
        return Approval.PENDING


@dataclass
class Connection(db.Model):
    username: str = db.Column(db.Text, primary_key=True)
    password: str = db.Column(db.Text, nullable=False)
    email: str = db.Column(db.String(50), nullable=True)
    approval: Approval = db.Column(Enum(Approval), nullable=False, default=_default_approval_from_config)


class ConnectionAdmin(sqla.ModelView):
    can_view_details = True

    column_list = ["username", "email", "approval"]

    column_searchable_list = ["username", "email"]

    column_editable_list = ["approval"]

    column_default_sort = [("username", True)]

    column_filters = ["username", "email", "approval"]

    form_columns = ("username", "password", "email")

    form_create_rules = ["username", "password", "email"]

    form_edit_rules = ["username", "email"]

    @action("approve", "Approve", "Are you sure you want to approve selection?")
    def approve_action(self, usernames):
        try:
            query = Connection.query.filter(Connection.username.in_(usernames))

            count = 0
            for conn in query.all():
                if conn.approval == Approval.PENDING:
                    conn.approval = Approval.APPROVED
                    count += 1
            db.session.commit()
            flash(
                ngettext(
                    "Connection was successfully approved.", "%(count)s connections were approved.", count, count=count
                )
            )

        except Exception:
            flash(gettext("Failed to approve connections."))

    @action("disapprove", "Disapprove", "Are you sure you want to disapprove selection?")
    def disapprove_action(self, usernames):
        try:
            query = Connection.query.filter(Connection.username.in_(usernames))

            count = 0
            for conn in query.all():
                if conn.approval == Approval.APPROVED:
                    conn.approval = Approval.PENDING
                    count += 1
            db.session.commit()
            flash(
                ngettext(
                    "Connection was successfully disapproved.",
                    "%(count)s connections were disapproved.",
                    count,
                    count=count,
                )
            )

        except Exception:
            flash(gettext("Failed to disapprove connections."))


class AuthAdmin(sqla.ModelView):
    can_view_details = True

    column_list = ["id", "url", "host", "username", "github", "approval"]

    column_searchable_list = ["username", "github", "host", "id"]

    column_editable_list = ["approval"]

    column_default_sort = [("username", True)]

    column_filters = ["username", "github", "host"]

    form_create_rules = [
        "username",
        "github",
        "host",
        "password",
    ]

    form_edit_rules = ["username", "github", "host"]

    @action("approve", "Approve", "Are you sure you want to approve selection?")
    def approve_action(self, ids):
        try:
            query = Author.query.filter(Author.id.in_(ids))

            count = 0
            for author in query.all():
                if author.approval == Approval.PENDING:
                    author.approval = Approval.APPROVED
                    count += 1
            db.session.commit()
            flash(ngettext("User was successfully approved.", "%(count)s users were approved.", count, count=count))

        except Exception as e:
            flash(gettext("Failed to approve users. Error {}".format(str(e))))
