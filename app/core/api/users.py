from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
