from django.urls import path
from .views import ExpenseListCreateView, RegisterView

urlpatterns = [
    path('expenses/', ExpenseListCreateView.as_view(), name='expenses'),
    path('register/', RegisterView.as_view(), name='register')
]