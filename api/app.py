from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from api.admin import admin_bp
from api.user import user_bp

# db must be initialized before importing models
db = SQLAlchemy()

from api.user.comments import model
from api.user.posts import model

# note: Heroku will run things from the working directory as the root of this repo. Therefore, this path MUST
# be relative to the root of the repo, NOT to this file. You will likely need to specify the working directory
# as the root of this repo # when you run this file in your IDE
app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
app.register_blueprint(user_bp, url_prefix="/authors")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

db.init_app(app)


@app.route("/")
def home_redirect():
    return redirect("/index.html", code=302)


@app.route("/hello_world")
def hello_world():
    return {"message": "Hello world"}


if __name__ == "__main__":
    db.create_all()
    app.run()
