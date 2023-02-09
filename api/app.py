from flask import Flask, redirect, url_for

from api.admin import admin_bp
from api.user import user_bp

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
app.register_blueprint(user_bp, url_prefix="/authors")
app.register_blueprint(admin_bp, url_prefix="/admin")


@app.route("/")
def home_redirect():
    return redirect("/index.html", code=302)


@app.route("/hello_world")
def hello_world():
    return {"message": "Hello world"}


if __name__ == "__main__":
    app.run()
