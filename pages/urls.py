from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('confirm', views.confirm, name='confirm'),
	path('admin/login', views.login, name='admin_login'),
	path('admin/logout', views.logout, name='admin_logout')
]
