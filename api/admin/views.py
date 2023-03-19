from flask_admin import BaseView, expose


class SettingsView(BaseView):
    @expose("/")
    def index(self):
        return self.render("settings.html")
