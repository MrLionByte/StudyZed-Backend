from django.http import JsonResponse

def health_check_action(request):
    return JsonResponse({"status": "ok"})