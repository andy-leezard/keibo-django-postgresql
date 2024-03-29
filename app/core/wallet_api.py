from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .serializers import KeiboUserSerializer, WalletSerializer
from .models import KeiboUser, Wallet, WalletUser
import uuid
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
        wallet = wallet_user.wallet
        asset = wallet.asset
        wallet_data = WalletSerializer(wallet).data
        wallet_data['role'] = wallet_user.role
        wallet_data['category'] = asset.category
        wallet_data['val_usd'] = float(wallet.balance * asset.exchange_rate)
        serialized_wallets.append(wallet_data)
    return Response(serialized_wallets)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet_owner(request, id=None):
    # Validate that wallet_id is provided and is in UUID format
    try:
        uuid.UUID(id)
    except ValueError:
        return Response(
            {'detail': 'Invalid wallet_id format. It should be a UUID.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = KeiboUser.objects.get(wallet=id)
        # Serialize the queryset
        serializer = KeiboUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except KeiboUser.DoesNotExist:
        return Response(
            {'detail': 'No user by this id is attached to this wallet.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
        instance: Wallet = self.get_object()
        # Check if the authenticated user is related to this wallet through a WalletUser
        wallet_user = WalletUser.objects.filter(
            user=request.user, wallet=instance
        ).first()  # exists()

        # If the wallet is not public and the user doesn't have access via WalletUser, raise PermissionDenied
        if not instance.is_public and not wallet_user:
            raise PermissionDenied("You do not have permission to access this wallet.")
        serializer = self.get_serializer(instance)
        data = serializer.data
        if wallet_user:
            data['role'] = wallet_user.role
        else:
            data['role'] = 0
        data['category'] = instance.asset.category
        data['val_usd'] = float(instance.balance * instance.asset.exchange_rate)
        return Response(data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet_user = WalletUser.objects.filter(
            user=request.user, wallet=instance
        ).first()
        if not wallet_user or wallet_user.role < 3:
            raise PermissionDenied("You do not have permission to update this wallet.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet_user = WalletUser.objects.filter(
            user=request.user, wallet=instance
        ).first()
        if not wallet_user or wallet_user.role != 4:
            raise PermissionDenied("You do not have permission to delete this wallet.")
        return super().destroy(request, *args, **kwargs)

