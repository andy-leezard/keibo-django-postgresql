from django.http import JsonResponse
import time


def ping(request):
    current_time = int(time.time() * 1000)  # Convert to milliseconds
    return JsonResponse({"message": current_time})
