from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from forms.models import Form
from items.models import Item
from orders.models import Order

class OrdersViewsTestCase(TestCase):	
	def test_index_data(self):
		fixtures = call_command('loaddata', 'orders_views_test_data.json', verbosity=0)
		order    = Order.objects.get(pk=1)
		session  = self.client.session
		session['user'] = 'admin'	
		session.save()
		url  = reverse('orders')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'orders/index.html')
		self.assertContains(resp, order.form.gym)
		del session['user']
		
	def test_index_no_data(self):
		session = self.client.session
		session['user'] = 'admin'	
		session.save()
		url  = reverse('orders')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'orders/index.html')
		self.assertContains(resp, 'No orders exist at this time.')
		del session['user']
		
	def test_view(self):
		fixtures = call_command('loaddata', 'orders_views_test_data.json', verbosity=0)
		order    = Order.objects.get(pk=1)
		url      = reverse('view', kwargs={'order_id':1})
		resp     = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'orders/show.html')
		self.assertContains(resp, '<h1>%s</h1>' % order.form.title)
		
	def test_export(self):
		fixtures = call_command('loaddata', 'orders_views_test_data.json', verbosity=0)
		order    = Order.objects.get(pk=1)
		url      = reverse('export', kwargs={'order_id':1})
		resp     = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp['Content-Type'], 'application/vnd.ms-excel')
		
	def test_login_get(self):
		url      = reverse('login', kwargs={'form_id':1})
		resp     = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'orders/login.html')
		
	def test_login_post(self):
		fixtures  = call_command('loaddata', 'orders_views_test_data.json', verbosity=0)
		order     = Order.objects.get(pk=1)
		url       = reverse('login', kwargs={'form_id':1})		
		test_data = {'user': order.form.email}
		resp      = self.client.post(url, test_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		self.assertEqual(resp.status_code, 200)
		url  = reverse('create', kwargs={'form_id':1})
		resp = self.client.post(url, test_data)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'orders/create.html')
		
	def test_create_post(self):		
		fixtures  = call_command('loaddata', 'orders_views_test_data.json', verbosity=0)
		order     = Order.objects.get(pk=1)
		url       = reverse('create_test', kwargs={'form_id':1})
		test_data = {
			'user':               order.form.email,
			'qty-item-1-size-1':  '1',
			'name-item-1-size-1': 'John Doe'
		}
		resp = self.client.post(url, test_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(Order.objects.all().count(), 2)
		url  = reverse('confirm')
		resp = self.client.get(url)
		self.assertTemplateUsed(resp, 'pages/confirm.html')