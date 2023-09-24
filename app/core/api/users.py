import json
from rest_framework import status, generics, response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from djoser.conf import settings
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.utils import ActionViewMixin
from django.http import JsonResponse
from ..serializers import KeiboUserSerializer
from ..models import KeiboUser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request, keyword=None):
    # keyword = request.query_params.get('keyword', '')
    # Filter users based on the keyword in email
    if keyword == None:
        return Response([], status=status.HTTP_200_OK)
    users = KeiboUser.objects.filter(email__icontains=keyword, is_active=True)
    # Serialize the queryset
    serializer = KeiboUserSerializer(users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


class KeiboUserUpdateView(generics.UpdateAPIView):
    queryset = KeiboUser.objects.all()
    serializer_class = KeiboUserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([AllowAny])
def check_user(request):
    # Get the WalletUser objects associated with the authenticated user
    post_data = json.loads(request.body.decode("utf-8"))
    if 'email' in post_data:
        try:
            user = KeiboUser.objects.get(email=post_data['email'])
        except KeiboUser.DoesNotExist:
            return JsonResponse({"exists": False})
        return JsonResponse({"exists": True, "activated": user.is_active})
    else:
        return JsonResponse({"detail": "Invalid email format"}, status=400)
