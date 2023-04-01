from api.utils import Approval


def _default_approval_from_config(context):
    return Approval.PENDING
