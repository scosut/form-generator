from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

def index(request):
	user = request.session.get('user', None)
	
	if user != 'admin':
		request.session['referer'] = reverse('index')
		return redirect(reverse('admin_login'))
	
	return render(request, 'pages/index.html', {'source': settings.STATIC_URL, 'colors': ['green', 'blue', 'orange', 'mustard'], 'isHome': True})

def confirm(request):
	return render(request, 'pages/confirm.html')

def login(request):
	if request.is_ajax():
		user     = request.POST.get("user", None)
		password = request.POST.get("password", None)
		referer  = request.session.get("referer", None)
		request.session['user'] = user
		
		if referer is None:
			referer = reverse('index')
			
		return JsonResponse({"url": referer})
	else:
		return render(request, 'pages/login.html')
	
def logout(request):
	keys = ['user', 'referer']
	
	for key in keys:		
		if request.session.has_key(key):
			del request.session[key]
		
	return login(request)