from django.urls import path
from . import views

urlpatterns = [
	path('create/<int:form_id>', views.create, {'isTest': False}, name='create'),
	path('create/<int:form_id>', views.create, {'isTest': True}, name='create_test'),
	path('view/<int:order_id>', views.view, name='view'),
	path('', views.index, name='orders'),
	path('login/<int:form_id>', views.login, name='login'),
	path('export/<int:order_id>', views.export, name='export'),
]
