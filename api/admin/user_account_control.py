from flask import flash
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext
from flask_admin.contrib import sqla

from api import db
from api.admin import RedirectingAuthMixin
from api.user.author.model import Author
from api.utils import Approval


class UserAccountControlView(RedirectingAuthMixin, sqla.ModelView):
    can_view_details = True

    column_list = ["id", "role", "url", "host", "username", "github", "approval"]

    column_searchable_list = ["username", "github", "host", "id"]

    column_editable_list = ["approval", "role"]

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
