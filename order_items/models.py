from django.db import models
from items.models import Item
from orders.models import Order

class OrderItem(models.Model):
	size     = models.CharField(max_length=255)
	quantity = models.IntegerField()	
	athletes = models.TextField()	
	order    = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
	item     = models.ForeignKey(Item, on_delete=models.DO_NOTHING)