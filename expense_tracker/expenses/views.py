from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from .serializer import ExpenserSerializer

# Create your views here.

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user = self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
