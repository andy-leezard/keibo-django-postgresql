from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import WalletSerializer
from .models import WalletUser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallets(request, role=None, range=None):
    # Get the WalletUser objects associated with the authenticated user
    wallet_users_query = WalletUser.objects.filter(user=request.user)

    # Convert role and range to integer if present
    role = int(role) if role is not None else None
    range = int(range) if range is not None else None

    # Apply role and range filters if needed
    if role is not None:
        if range is None or range == 0:
            wallet_users_query = wallet_users_query.filter(role=role)
        elif range < 0:
            wallet_users_query = wallet_users_query.filter(
                role__lte=role, role__gte=role + range
            )
        else:
            wallet_users_query = wallet_users_query.filter(
                role__gte=role, role__lte=role + range
            )

    # Get the Wallet objects associated with the wallet_users
    wallets = [wallet_user.wallet for wallet_user in wallet_users_query]

    serializer = WalletSerializer(wallets, many=True)
    return Response(serializer.data)
