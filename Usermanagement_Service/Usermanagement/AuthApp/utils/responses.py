from rest_framework.response import Response


def api_response(success, message, data={}, error=None,auth_status=None, status_code=None):
    response_structure = {
        "success": success,
        "message": message,
        "data": data,
        "auth-status": auth_status,
        "error": error
    }
    return Response(response_structure, status=status_code)