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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_balance = None

        # Before saving, check if confirmed_by_recipient or confirmed_by_sender is updated
        if 'confirmed_by_recipient' in request.data and instance.recipient:
            if request.data['confirmed_by_recipient']:
                instance.recipient.balance -= instance.net_amount
                instance.recipient.save()
                new_balance = instance.recipient.balance
            else:
                instance.recipient.balance += instance.net_amount
                instance.recipient.save()
                new_balance = instance.recipient.balance

        if 'confirmed_by_sender' in request.data and instance.sender:
            if request.data['confirmed_by_sender']:
                instance.sender.balance += instance.net_amount
                instance.sender.save()
                new_balance = instance.sender.balance
            else:
                instance.sender.balance -= instance.net_amount
                instance.sender.save()
                new_balance = instance.sender.balance

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # Append 'new_balance' to the response data
        data = dict(serializer.data)
        if new_balance is not None:
            data['new_balance'] = float(new_balance)

        return Response(data)
