from flask import redirect, render_template
from flask_login import current_user

from api.utils import Role


class RedirectingAuthMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated and not current_user.role == Role.ADMIN:
            return render_template("not_admin_page.html")
        return redirect("/login")
