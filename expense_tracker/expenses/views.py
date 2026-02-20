from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.timezone import now
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

class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_date = now()
        month = current_date.month
        year = current_date.year

        expenses = Expense.objects.filter(
            user = request.user,
            created_at__month = month,
            created_at__year = year
        )

        total = expenses.aggregate(total_amount = Sum("amount"))["total_amount"] or 0
        count = expenses.count()

        return Response({
            "month" : month,
            "year" : year,
            "total_expense" : total,
            "count" : count
        })
