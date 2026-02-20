from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Expense
from .serializer import ExpenserSerializer, RegisterSerializer

# Create your views here.

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenserSerializer
    permission_classes = [IsAuthenticated]


    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    lookup_fields = ['category','amount']
    ordering_fields = ['amount', 'created_at']

    def get_queryset(self):
        return Expense.objects.filter(user = self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []
