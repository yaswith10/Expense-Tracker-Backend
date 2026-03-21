from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Expense
from .serializer import ExpenseSerializer, RegisterSerializer


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category", "amount"]
    ordering_fields = ["amount", "created_at"]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []


class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_date = now()
        expenses = Expense.objects.filter(
            user=request.user,
            created_at__month=current_date.month,
            created_at__year=current_date.year,
        )
        total = expenses.aggregate(total_amount=Sum("amount"))["total_amount"] or 0
        count = expenses.count()
        return Response({
            "month": current_date.month,
            "year": current_date.year,
            "total_expense": total,
            "count": count,
        })


class ExpenseCategoryBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_date = now()
        expenses = Expense.objects.filter(
            user=request.user,
            created_at__month=current_date.month,
            created_at__year=current_date.year,
        )
        breakdown = (
            expenses
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        return Response({
            "month": current_date.month,
            "year": current_date.year,
            "breakdown": list(breakdown),
        })
