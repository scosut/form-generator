from django.db import models
from forms.models import Form

def get_upload_path(instance, filename):
	return 'forms/'+str(instance.form.id)+'/'+filename

class Item(models.Model):
	order = models.IntegerField()
	title = models.CharField(max_length=255)
	price = models.IntegerField()
	image = models.ImageField(upload_to=get_upload_path)
	sizes = models.TextField()
	form  = models.ForeignKey(Form, on_delete=models.DO_NOTHING)