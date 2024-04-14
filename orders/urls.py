from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend.urls')),
]