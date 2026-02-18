from rest_framework import serializers
from .models import Expense

class ExpenserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['user', 'created_at']