from rest_framework import serializers
from .models import Payment, Transaction, Service

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'status', 'created_at', 'updated_at', 'user']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'payment', 'transaction_id', 'amount', 'status', 'created_at']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price']