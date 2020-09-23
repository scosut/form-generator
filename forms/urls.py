from django.urls import path
from . import views

urlpatterns = [
	path('add', views.add, name='add'),
	path('edit/<int:form_id>', views.edit, name='edit'),
	path('', views.index, name='forms'),
	path('notify/<int:form_id>', views.notify, {'isTest': False}, name='notify'),
	path('notify/<int:form_id>', views.notify, {'isTest': True}, name='notify_test')
]
