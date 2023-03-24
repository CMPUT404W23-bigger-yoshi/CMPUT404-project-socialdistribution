from flask import redirect
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user

from api.utils import Role


class SettingsView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return super().inaccessible_callback(name, **kwargs)

    @expose("/")
    def index(self):
        return self.render("settings.html")


class Logout(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")
