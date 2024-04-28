from django.conf import settings
from django.conf.urls.static import static
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
    path('user_image/<int:pk>/', views.upload_user_image, name='user_image'),
    path('product_image/<int:pk>/', views.upload_product_image, name='product_image'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )