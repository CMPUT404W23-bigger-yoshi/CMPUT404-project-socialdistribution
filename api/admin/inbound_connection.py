from dataclasses import dataclass

from flask import flash, redirect
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext
from flask_admin.contrib import sqla
from flask_login import current_user
from sqlalchemy import Enum

from api import db
from api.admin import RedirectingAuthMixin
from api.utils import Approval, Role


def _default_approval_from_config(context):
    return Approval.PENDING


@dataclass
class InboundConnection(db.Model):
    """
    These are *inbound* connection parameters, ie, the credentials we distribute to other nodes to connect to us
    """

    username: str = db.Column(db.Text, primary_key=True)
    password: str = db.Column(db.Text, nullable=False)
    email: str = db.Column(db.Text, nullable=True)
    # note (matt): why does this have an approval flag? if we give credentials, isn't that approval already. w/e
    approval: Approval = db.Column(Enum(Approval), nullable=False, default=_default_approval_from_config)


class InboundConnectionView(RedirectingAuthMixin, sqla.ModelView):
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
            query = InboundConnection.query.filter(InboundConnection.username.in_(usernames))

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
            query = InboundConnection.query.filter(InboundConnection.username.in_(usernames))

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
