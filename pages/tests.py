from django.test import TestCase
from django.urls import reverse

class PagesViewsTestCase(TestCase):	
	def test_index(self):
		session = self.client.session
		session['user'] = 'admin'	
		session.save()
		url  = reverse('index')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'pages/index.html')
		self.assertContains(resp, '<h1>Form Builder</h1>')
		del session['user']
		
	def test_confirm(self):
		url  = reverse('confirm')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'pages/confirm.html')
		self.assertContains(resp, '<h1>Thank You!</h1>')
		
	def test_login_get(self):
		url  = reverse('admin_login')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'pages/login.html')
		self.assertContains(resp, '<h1>Administrator Login</h1>')
		
	def test_login_post(self):		
		url       = reverse('admin_login')
		test_data = {
			'user':     'admin',
			'password': 'admin'
		}
		resp = self.client.post(url, test_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		req  = resp.wsgi_request
		self.assertEqual(resp.status_code, 200)		
		self.assertEqual(req.session['user'], test_data['user'])
		url  = reverse('index')
		resp = self.client.get(url)
		self.assertContains(resp, '<h1>Form Builder</h1>')
		
	def test_logout(self):
		url  = reverse('admin_logout')
		resp = self.client.get(url)		
		req  = resp.wsgi_request
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(len(req.session.keys()), 0)
		self.assertTemplateUsed(resp, 'pages/login.html')
		self.assertContains(resp, '<h1>Administrator Login</h1>')