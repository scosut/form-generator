from django.core.management import call_command
from django.test import TestCase
from forms.models import Form
from items.models import get_upload_path, Item

class ItemTestCase(TestCase):	
	def test_get_upload_path(self):
		fixtures = call_command('loaddata', 'items_models_testdata.json', verbosity=0)
		item     = Item.objects.get(pk=1)
		filename = 'test'
		path     = get_upload_path(item, filename)
		self.assertEqual(path, 'forms/%s/%s' % (item.form.id, filename))