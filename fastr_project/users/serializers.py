from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from dj_rest_auth.serializers import PasswordResetSerializer

from api.models import Cart
from users.models import User
from users.tasks import user_registered_email, user_password_reset_email


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):

        user_password_reset_email.delay(
            user_id=context.get('user').id,
            uid=context.get('uid'),
            token=context.get('token'),
        )


class CustomPasswordResetSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        return CustomPasswordResetForm


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

        errors = {}
        try:
            validate_password(password=password, user=user)
        except DjangoValidationError as error:
            errors['password'] = list(error.messages)
        if errors:
            raise DjangoValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        if user.type == 'buyer':
            Cart.objects.create(user=user)

        user_registered_email.delay(user.id)

        return user

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'company', 'position', 'type')
        extra_kwargs = {'password': {'write_only': True}}
