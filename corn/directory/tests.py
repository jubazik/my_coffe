from django.test import TestCase
from .models import *


for order in OrderTable.objects.all():
    order = order.table.orderitem_set.all()
    print(order)

# Create your tests here.
