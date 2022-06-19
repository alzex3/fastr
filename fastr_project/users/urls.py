from django.urls import path

from rest_framework_simplejwt.views import TokenVerifyView

from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import (
    LoginView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView,
)

from users.views import UserCreateView


app_name = 'users'

urlpatterns = [

    # URLs that require token auth
    path('profile/', UserDetailsView.as_view(), name='user_details'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),

    # URLs that do not require token auth
    path('registration/', UserCreateView.as_view(), name='registration'),
    path('token/create/', LoginView.as_view(), name='token_create'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),

]
