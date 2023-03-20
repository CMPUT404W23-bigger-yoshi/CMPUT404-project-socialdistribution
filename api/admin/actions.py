from flask import Blueprint, request

from api.admin.APIConfig import APIConfig

actions_bp = Blueprint("actions", __name__)


@actions_bp.route("/config", methods=["POST"])
def modify_config():
    form_data = request.form

    api_protect = form_data.get("API")
    author_auto = form_data.get("Approve-authors")
    nodes_auto = form_data.get("Approve-nodes")
    node_limit = form_data.get("Node-limit")

    if api_protect:
        APIConfig.set_API_protection(True)
    else:
        APIConfig.set_API_protection(False)

    if author_auto:
        APIConfig.set_author_approval(True)
    else:
        APIConfig.set_author_approval(False)

    if nodes_auto:
        APIConfig.set_node_approval(True)
    else:
        APIConfig.set_node_approval(False)

    if node_limit:
        val = int(node_limit)
        if val >= 0:
            APIConfig.set_node_limit(val)

    APIConfig.reload()
    return {"message": "Success"}, 200
