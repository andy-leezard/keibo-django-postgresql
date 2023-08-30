from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction, Wallet
from .serializers import TransactionSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import uuid


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request, wallet_id):
    # Validate that wallet_id is provided and is in UUID format
    try:
        uuid.UUID(wallet_id)
    except ValueError:
        return Response(
            {'detail': 'Invalid wallet_id format. It should be a UUID.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get the WalletUser objects associated with the authenticated user
    transactions_query = Transaction.objects.filter(
        Q(recipient=wallet_id) | Q(sender=wallet_id)
    )

    serialized_transactions = TransactionSerializer(transactions_query, many=True).data
    return Response(serialized_transactions)


class TransactionCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance: Transaction = serializer.save()
        retro = self.request.query_params.get('retro')
        if retro:
            pass
        else:
            if instance.recipient != None:
                try:
                    recipient_wallet = Wallet.objects.get(id=instance.recipient)
                    recipient_wallet.balance += instance.net_amount
                    recipient_wallet.save()
                except Wallet.DoesNotExist:
                    pass
                except ObjectDoesNotExist:
                    pass
            if instance.sender != None:
                try:
                    sender_wallet = Wallet.objects.get(id=instance.sender)
                    sender_wallet.balance -= instance.net_amount
                    sender_wallet.save()
                except Wallet.DoesNotExist:
                    pass
                except ObjectDoesNotExist:
                    pass

class TransactionUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]



