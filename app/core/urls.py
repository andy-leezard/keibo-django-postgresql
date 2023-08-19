from django.urls import path, re_path, register_converter
from core.api.users import search_users
from .wallet_api import get_wallets, WalletCreateView, WalletUpdateView
from .utils import NegativeIntConverter
from .healthcheck import ping
from .views import (
    hello_world,
    CustomProviderAuthView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
)

register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
    re_path(
        r'^o/(?P<provider>\S+)/$',
        CustomProviderAuthView.as_view(),
        name='provider-auth',
    ),
    path("hello_world/", hello_world, name="hello_world"),
    path("ping/", ping, name="ping"),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),
    # --
    # path('get_wallets/<str?:role>/<int?:range>', get_wallets, name="get_wallets"), ==
    # re_path(
    #     r'^get_wallets/(?P<role>\w+)?/(?P<range>\d+)?/$',
    #    get_wallets,
    #    name="get_wallets",
    # ),
    path('search_users/<str:keyword>/', search_users, name="search_users"),
    path('wallet/', WalletCreateView.as_view(), name='wallet-list-create'),
    path('wallet/<uuid:pk>/', WalletUpdateView.as_view(), name='wallet-rud'),
    path('get_wallets/', get_wallets, name="get_wallets_no_params"),
    path('get_wallets/<str:role>/', get_wallets, name="get_wallets_role"),
    path(
        'get_wallets/<str:role>/<negint:range>/', get_wallets, name="get_wallets_both"
    ),
]
