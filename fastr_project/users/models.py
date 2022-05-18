import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


USER_TYPE_CHOICES = (
    ('seller', 'Seller'),
    ('buyer', 'Buyer'),
    ('staff', 'Staff'),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address!')
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        verbose_name='Email',
        blank=False,
        unique=True,
        validators=[validators.validate_email],
    )
    company = models.CharField(
        verbose_name='Company',
        max_length=40,
        blank=True,
    )
    position = models.CharField(
        verbose_name='Position',
        max_length=40,
        blank=True,
    )
    type = models.CharField(
        verbose_name='User type',
        choices=USER_TYPE_CHOICES,
        max_length=6,
        default='buyer',
    )

    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('type',)

    def __str__(self):
        return self.email
