from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('poll/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
