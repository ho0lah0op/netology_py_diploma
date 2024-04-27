from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from backend import views

router_v1 = DefaultRouter()

urlpatterns = [
    path('', views.home_page, name='index'),
    path('', include('social_django.urls', namespace='social')),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend.urls')),
]