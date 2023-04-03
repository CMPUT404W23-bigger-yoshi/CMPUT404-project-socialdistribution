from flask import Blueprint, request, current_app, send_file, make_response
import os, base64
from pathlib import Path
from werkzeug.utils import secure_filename
from api import db, API_BASE
from api.utils import generate_object_ID

image_table = db.Table(
    "images",
    db.Column("id", db.Text, primary_key=True, default=generate_object_ID),
    db.Column("image", db.Text),
    db.Column("mimeType", db.Text)
)

images_bp = Blueprint("images", __name__)

@images_bp.route("/upload/", methods=['POST'])
def upload():
    if not request.files:
        return {"message": "No file"}, 400
    file = request.files['data']
    mime = file.content_type
    id = generate_object_ID()
    stmt = image_table.insert().values(id=id, image=file.read(), mimeType=mime)
    db.session.execute(stmt)
    db.session.commit()

    return {"message": "Uploaded successfully" ,"URI": API_BASE + "resources/" + id + "/image"}, 201

@images_bp.route("/resources/<string:image_id>/image", methods=['GET'])
def image_as_b64(image_id):
    stmt = image_table.select().where(image_table.c.id==image_id)
    img = db.session.execute(stmt).fetchone()
    if not img:
        return {"message": "No image"}, 400
    response = make_response(img.image)
    response.headers.set('Content-Type', img.mimeType)
    return response, 200

