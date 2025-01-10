from rest_framework.response import Response


def api_response(status_code ,message ,data ,auth_status=None ,errors=None):
    response = {
        "status"        : status_code,
        "message"       : message,
        "data"          : data or {},
        "auth-status"   : auth_status,
        "errors": errors or {},
    }
    return Response(response)
