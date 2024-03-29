from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import UserViewSet

app_name = 'backend'
router_v1 = DefaultRouter()

router_v1.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    ]
