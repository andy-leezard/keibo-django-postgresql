from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .serializers import WalletSerializer
from .models import Wallet, WalletUser
from django.db.models import Q
import time


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
    serialized_wallets = WalletSerializer(wallets, many=True).data

    # Attach the role property from the corresponding WalletUser model
    serialized_wallets = []
    for wallet_user in wallet_users_query:
        wallet_data = WalletSerializer(wallet_user.wallet).data
        wallet_data['role'] = wallet_user.role
        serialized_wallets.append(wallet_data)

    return Response(serialized_wallets)


class WalletCreateView(generics.ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        wallet = serializer.save()
        WalletUser.objects.create(
            user=self.request.user,
            wallet=wallet,
            role=4,
            granted_at=int(time.time() * 1000),
        )


class WalletUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the authenticated user is related to this wallet through a WalletUser
        user_has_access = WalletUser.objects.filter(user=request.user, wallet=instance).exists()

        # If the wallet is not public and the user doesn't have access via WalletUser, raise PermissionDenied
        if not instance.is_public and not user_has_access:
            raise PermissionDenied("You do not have permission to access this wallet.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet_user = WalletUser.objects.filter(user=request.user, wallet=instance).first()
        if not wallet_user or wallet_user.role < 3:
            raise PermissionDenied("You do not have permission to update this wallet.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet_user = WalletUser.objects.filter(user=request.user, wallet=instance).first()
        if not wallet_user or wallet_user.role != 4:
            raise PermissionDenied("You do not have permission to delete this wallet.")
        return super().destroy(request, *args, **kwargs)

