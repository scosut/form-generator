from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [	
	path('orders/', include('orders.urls')),
	path('forms/', include('forms.urls')),	
	path('', include('pages.urls')),
  path('admin/', admin.site.urls)
]
