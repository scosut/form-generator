from django.db import models

class Form(models.Model):
	title        = models.CharField(max_length=255)
	instructions = models.TextField()
	logo         = models.ImageField(upload_to='logos/')
	email        = models.CharField(max_length=255)
	gym          = models.CharField(max_length=255)
	forSale      = models.IntegerField()	
	notified     = models.DateTimeField(null=True)