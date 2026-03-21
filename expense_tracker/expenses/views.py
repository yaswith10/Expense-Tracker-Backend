import hashlib
import json
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Sum
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from .ai.exceptions import AIModuleError, LLMRateLimitError
from .ai.interface import ExpenseData, get_expense_insights
from .models import Expense
from .serializer import ExpenseSerializer, RegisterSerializer

_INSIGHTS_CACHE_TTL_SECONDS = 900  # 15 minutes
_INSIGHTS_EXPENSE_LIMIT = 30


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


class ExpenseInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = (
            Expense.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .values("title", "amount", "category", "date")
            [:_INSIGHTS_EXPENSE_LIMIT]
        )

        if not expenses:
            return Response({"insights": [], "source": "none", "cached": False})

        cache_key = self._build_cache_key(request.user.id, list(expenses))
        cached = cache.get(cache_key)
        if cached is not None:
            return Response({**cached, "cached": True})

        expense_data = [
            ExpenseData(
                title=e["title"],
                amount=Decimal(str(e["amount"])),
                category=e["category"],
                date=e["date"],
            )
            for e in expenses
        ]

        try:
            result = get_expense_insights(expense_data)
        except LLMRateLimitError:
            return Response(
                {"error": "The AI service is temporarily rate-limited. Please try again shortly."},
                status=429,
            )
        except AIModuleError as exc:
            return Response(
                {"error": "AI insights are temporarily unavailable.", "detail": str(exc)},
                status=503,
            )

        payload = {"insights": result.insights, "source": result.source}
        cache.set(cache_key, payload, timeout=_INSIGHTS_CACHE_TTL_SECONDS)

        return Response({**payload, "cached": False})

    @staticmethod
    def _build_cache_key(user_id: int, expenses: list[dict]) -> str:
        fingerprint = json.dumps(expenses, default=str, sort_keys=True)
        digest = hashlib.sha256(fingerprint.encode()).hexdigest()
        return f"expense_insights:{user_id}:{digest}"
