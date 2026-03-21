from django.urls import path
from .views import (
    ExpenseListCreateView,
    ExpenseDetailView,
    ExpenseCategoryBreakdownView,
    ExpenseInsightsView,
    RegisterView,
    ExpenseSummaryView,
)

urlpatterns = [
    path("expenses/", ExpenseListCreateView.as_view(), name="expenses"),
    path("expenses/summary/", ExpenseSummaryView.as_view(), name="expense-summary"),
    path("expenses/category-breakdown/", ExpenseCategoryBreakdownView.as_view(), name="expense-category-breakdown"),
    path("expenses/insights/", ExpenseInsightsView.as_view(), name="expense-insights"),
    path("expenses/<int:pk>/", ExpenseDetailView.as_view(), name="expense-detail"),
    path("register/", RegisterView.as_view(), name="register"),
]
