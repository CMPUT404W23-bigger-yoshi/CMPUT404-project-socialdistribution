from flask import Blueprint

from api.admin.APIConfig import APIConfig

actions_bp = Blueprint("actions", __name__)


@actions_bp.route("/protection/<int:val>", methods=["POST"])
def modify_api_protection(val):
    value = True if val == 1 else False
    APIConfig.set_API_protection(value)
    return {"message", "API Protection modified."}, 200


@actions_bp.route("/auth-approval/<int:val>", methods=["POST"])
def modify_author_approval(val):
    value = True if val == 1 else False
    APIConfig.set_author_approval(value)
    return {"message", "Author Auto-approval rule modified."}, 200


@actions_bp.route("/node-approval/<int:val>", methods=["POST"])
def modify_node_approval(val):
    value = True if val == 1 else False
    APIConfig.set_node_approval(value)
    return {"message": "Node Auto-approval rule modified."}, 200


@actions_bp.route("/node-limit/<int:val>", methods=["POST"])
def modify_node_limit(val):
    if val < 0:
        return {"message": "Invalid node limit"}, 400
    APIConfig.set_node_limit(val)
    return {"message": "Node limit changed."}, 200
