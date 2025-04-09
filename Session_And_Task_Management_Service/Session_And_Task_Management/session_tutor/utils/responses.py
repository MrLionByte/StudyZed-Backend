from rest_framework.response import Response


def api_response(status_code ,message=None ,data=None ,auth_status=None ,errors=None):
    response = {
        "status"        : status_code,
        "message"       : message or {},
        "data"          : data or {},
        "auth-status"   : auth_status,
        "errors": errors or {},
    }
    print(status_code)
    return Response(response,status=status_code)
