from django.db import models
from forms.models import Form

class Order(models.Model):
	orderDate = models.DateTimeField(auto_now=True)
	form      = models.ForeignKey(Form, on_delete=models.DO_NOTHING)