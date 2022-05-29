from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import RegisterUserSerializer


class UserCreateView(CreateAPIView):
    """
    Creates new user.
    """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)
