from django.urls import path

from .views import *

urlpatterns = [
    path('orders/create/', create_order, name='create_order'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/edit/', edit_order, name='edit_order'),
    path('orders/',order_list, name='order_list'),
    path('pay_list', cashreceiptorderviews, name='pay_list'),
    path('orders/<int:order_id>/pay/', mark_order_as_paid, name='pay_order'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
]