from django.urls import path
from .views import ExpenseListCreateView, RegisterView, ExpenseSummaryView

urlpatterns = [
    path('expenses/', ExpenseListCreateView.as_view(), name='expenses'),
    path('expenses/summary/', ExpenseSummaryView.as_view(), name='expense-summary'),
    path('register/', RegisterView.as_view(), name='register'),
]