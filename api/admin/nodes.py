from flask import Blueprint, request

from api import db
from api.admin.APIConfig import APIConfig
from api.admin.model import Connection

nodes_bp = Blueprint("node", __name__)


@nodes_bp.route("/register", methods=["POST"])
def register_node():
    """
    Register another service to connect with bigger-yoshi
    and start using our api.
    """
    data = request.json
    username = data.get("hostname", None)
    password = data.get("password", None)
    email = data.get("email", None)

    count = Connection.query.count()
    if count >= APIConfig.NODE_LIMIT:
        return {"message": "Maximum nodes connected."}, 503

    if not username or not password:
        return {"message": "Invalid Credentials"}, 400

    host_exists = Connection.query.filter_by(username=username).first()
    if host_exists:
        return {"message": "Service already connected."}, 409

    connnection = Connection(username=username, password=password, email=email)

    db.session.add(connnection)
    db.session.commit()

    return {"message": "Service connected succesfully."}, 200
