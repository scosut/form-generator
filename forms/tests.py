from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from forms.models import Form
from items.models import Item
import datetime
import os

class FormsViewsTestCase(TestCase):	
	def test_index_data(self):
		fixtures = call_command('loaddata', 'forms_views_testdata.json', verbosity=0)
		form     = Form.objects.get(pk=1)
		session  = self.client.session
		session['user'] = 'admin'	
		session.save()
		url  = reverse('forms')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'forms/index.html')
		self.assertContains(resp, form.gym)
		del session['user']
		
	def test_index_no_data(self):
		session = self.client.session
		session['user'] = 'admin'	
		session.save()
		url  = reverse('forms')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'forms/index.html')
		self.assertContains(resp, 'No forms exist at this time.')
		del session['user']
		
	def test_notify(self):
		fixtures = call_command('loaddata', 'forms_views_testdata.json', verbosity=0)
		url      = reverse('notify_test', kwargs={'form_id':1})
		form     = Form.objects.get(pk=1)
		old_date = form.notified
		resp     = self.client.get(url)
		form.refresh_from_db()
		new_date = form.notified
		self.assertEqual(new_date > old_date, True)
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(resp['Location'], reverse('forms'))
		
	def test_add_get(self):
		session  = self.client.session
		session['user'] = 'admin'	
		session.save()
		url  = reverse('add')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'forms/add.html')
		self.assertContains(resp, '<h1>New Form</h1>')
		del session['user']
		
	def test_add_post(self):		
		fixtures = call_command('loaddata', 'forms_views_testdata.json', verbosity=0)
		session  = self.client.session
		session['user'] = 'admin'
		session.save()		
		filename = os.path.join(os.path.dirname(__file__), 'test.png')
		image    = SimpleUploadedFile(name='test.png', content=open(filename, 'rb').read(), content_type='image/png')
		url = reverse('add')
		test_data = {
			'title':            'title test',
			'instructions':     'instructions test',
			'logo':             'logo test',
			'email':            'test@gmail.com',
			'gym':              'gym test',
			'for-sale':         '1',
			'item-title-1':     'item title 1 test',
			'item-price-1':     '5',
			'item-image-file-1': image,
			'item-sizes-1':     'item sizes 1 test'
		}
		resp = self.client.post(url, test_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}, format='multipart')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(Form.objects.all().count(), 2)
		url  = reverse('forms')
		resp = self.client.get(url)
		self.assertContains(resp, test_data['gym'])
		del session['user']
		
	def test_edit_get(self):
		fixtures = call_command('loaddata', 'forms_views_testdata.json', verbosity=0)
		session  = self.client.session
		session['user'] = 'admin'
		session.save()
		url  = reverse('edit', kwargs={'form_id':1})
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'forms/edit.html')
		self.assertContains(resp, '<h1>Edit Form</h1>')
		del session['user']
		
	def test_edit_post(self):		
		fixtures = call_command('loaddata', 'forms_views_testdata.json', verbosity=0)
		session  = self.client.session
		session['user'] = 'admin'
		session.save()		
		url  = reverse('edit', kwargs={'form_id':1})
		item = Item.objects.get(form_id=1)
		form = item.form
		test_data = {
			'title':             form.title,
			'instructions':      form.instructions,
			'logo':              str(form.logo),
			'email':             form.email,
			'gym':               'updated gym name',
			'for-sale':          form.forSale,
			'item-title-1':      item.title,
			'item-price-1':      str(item.price),
			'item-image-file-1': item.image,
			'item-sizes-1':      item.sizes
		}
		resp = self.client.post(url, test_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		self.assertEqual(resp.status_code, 200)
		form.refresh_from_db()
		self.assertEqual(form.gym, test_data['gym'])		
		url  = reverse('forms')
		resp = self.client.get(url)
		self.assertContains(resp, test_data['gym'])
		del session['user']