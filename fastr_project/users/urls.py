from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserCreateViewSet


router = DefaultRouter()
router.register('registration', UserCreateViewSet)

urlpatterns = [
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/', include(router.urls), name='user-registration'),
]
