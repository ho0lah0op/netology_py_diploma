from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import UserViewSet, ConfirmUserViewSet


app_name = 'backend'
router_v1 = DefaultRouter()

router_v1.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('user/register', UserViewSet.as_view({'post': 'create'}), name='user-register'),
    path('user/details', UserViewSet.as_view({'get': 'list'}), name='user-details'),
    path('user/register/confirm', ConfirmUserViewSet.as_view(), name='user-register-confirm'),
    # path('user/login', LoginAccount.as_view(), name='user-login'),
    # path('user/contact', ContactView.as_view(), name='user-contact'),
    # path('user/password_reset', reset_password_request_token, name='password-reset'),
    # path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),

    # path('user/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    ]
