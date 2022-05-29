from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from dj_rest_auth.serializers import PasswordResetSerializer

from api.models import Cart
from users.models import User
from users.tasks import user_registered_notification


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        extra_context = {
            'site_name': settings.SITE_NAME,
        }

        return {
            'email_template_name': 'password_reset_message.txt',
            'extra_email_context': extra_context,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'company', 'position', 'type')
        read_only_fields = ('type',)


class RegisterUserSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = User(**data)
        password = data.get('password')
        user_type = data.get('type')

        if user_type == 'staff':
            raise DjangoValidationError(
                'Failed! Register staff users through requests is restricted!'
            )

        errors = dict()
        try:
            validate_password(password=password, user=user)
        except DjangoValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise DjangoValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        if user.type == 'buyer':
            Cart.objects.create(user=user)

        user_registered_notification.delay(user.id)

        return user

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'company', 'position', 'type')
        extra_kwargs = {'password': {'write_only': True}}
