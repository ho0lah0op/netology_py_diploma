from django.urls import path, include
from django_rest_passwordreset.views import (
    reset_password_request_token,
    reset_password_confirm
)
from rest_framework.routers import SimpleRouter
from backend.views import (
    BasketViewSet,
    CategoryViewSet,
    ConfirmAccount,
    ContactViewSet,
    LoginAccountViewSet,
    OrderViewSet,
    PartnerOrdersViewSet,
    PartnerStateViewSet,
    PartnerUpdateViewSet,
    ProductInfoViewSet,
    ShopViewSet,
    UserViewSet
)

app_name = 'backend'

router_v1 = SimpleRouter()

router_v1.register(
    'user/contact',
    ContactViewSet,
    basename='user-contact'
)
router_v1.register(
    'user',
    UserViewSet,
    basename='user'
)
router_v1.register(
    'categories',
    CategoryViewSet,
    basename='user-category'
)
router_v1.register(
    'shops',
    ShopViewSet,
    basename='shops'
)
router_v1.register(
    'basket',
    BasketViewSet,
    basename='basket'
)
router_v1.register(
    r'order',
    OrderViewSet,
    basename='order'
)
router_v1.register(
    'partner/update',
    PartnerUpdateViewSet,
    basename='partner-update'
)
router_v1.register(
    r'partner/orders',
    PartnerOrdersViewSet,
    basename='partner-orders'
)
router_v1.register(
    r'partner/state',
    PartnerStateViewSet,
    basename='partner-state'
)

urlpatterns = [
    path(
        'user/register',
        UserViewSet.as_view({'post': 'create'}),
        name='user-register'
    ),
    path(
        'user/register/confirm',
        ConfirmAccount.as_view(),
        name='user-register-confirm'
    ),
    path(
        'user/login',
        LoginAccountViewSet.as_view({'post': 'create'}),
        name='user-login'
    ),
    path(
        'user/details/<int:id>/',
        UserViewSet.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'patch': 'update'
            }
        ),
        name='user-details'
    ),
    path(
        'user/password_reset',
        reset_password_request_token,
        name='password-reset'
    ),
    path(
        'user/password_reset/confirm',
        reset_password_confirm,
        name='password-reset-confirm'
    ),
    path(
        'order/confirm/',
        OrderViewSet.as_view({'post': 'confirm_order'}),
        name='confirm_order'
    ),
    path('order/assemble/',
         OrderViewSet.as_view({'post': 'assemble_order'}),
         name='assemble-order'
         ),
    path('order/send/',
         OrderViewSet.as_view({'post': 'send_order'}),
         name='send-order'
         ),
    path('order/deliver/',
         OrderViewSet.as_view({'post': 'deliver_order'}),
         name='deliver-order'
         ),
    path('order/cancel/',
         OrderViewSet.as_view({'post': 'cancel_order'}),
         name='cancel-order'
         ),
    path(
        'products',
        ProductInfoViewSet.as_view({'get': 'list'}),
        name='shops'
    ),
    path('user/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]