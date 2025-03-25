from django.urls import path
from .views import (
    ExpenseOrderListView,
    ExpenseOrderCreateView,
    ExpenseOrderUpdateView,
    ExpenseOrderDetailView,
    ExpenseOrderApproveView,
    execute_order,
)

urlpatterns = [
    path('', ExpenseOrderListView.as_view(), name='expense_order_list'),
    path('create/', ExpenseOrderCreateView.as_view(), name='expense_order_create'),
    path('<int:pk>/', ExpenseOrderDetailView.as_view(), name='expense_order_detail'),
    path('<int:pk>/edit/', ExpenseOrderUpdateView.as_view(), name='expense_order_edit'),
    path('<int:pk>/approve/', ExpenseOrderApproveView.as_view(), name='expense_order_approve'),
    path('<int:pk>/execute/', execute_order, name='expense_order_execute'),
]