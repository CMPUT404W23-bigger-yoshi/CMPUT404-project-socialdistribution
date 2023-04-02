from flask import redirect, render_template
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user

from api.admin import RedirectingAuthMixin


class SettingsView(RedirectingAuthMixin, BaseView):
    @expose("/")
    def index(self):
        return self.render(
            "settings.html",
        )


class Logout(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/login")
