import pytest

from rest_framework.test import APIClient

from model_bakery import baker

from api.models import Cart, ShippingNote


@pytest.fixture
def seller_user(django_user_model):
    seller_user = django_user_model.objects.create(
        password='12367FR',
        email='selleruser@gmail.com',
        first_name='Dmitri',
        last_name='Kapralov',
        position='Manager',
        company='Intel',
        type='seller',
    )
    return seller_user


@pytest.fixture
def buyer_user(django_user_model):
    buyer_user = django_user_model.objects.create(
        password='123AS743',
        email='buyeruser@gmail.com',
        first_name='Alexey',
        last_name='Zharinov',
        position='CTO',
        company='AMD',
        type='buyer',
    )

    Cart.objects.create(user=buyer_user)

    return buyer_user


@pytest.fixture
def anon_client(buyer_user):
    return APIClient()


@pytest.fixture
def seller_client(seller_user):
    client = APIClient()
    client.force_authenticate(user=seller_user)
    return client


@pytest.fixture
def buyer_client(buyer_user):
    client = APIClient()
    client.force_authenticate(user=buyer_user)
    return client


@pytest.fixture
def model_create():

    def factory(model, *args, **kwargs):
        return baker.make(model, make_m2m=True, _fill_optional=True, *args, **kwargs)

    return factory


@pytest.fixture
def model_prepare():

    def factory(model, *args, **kwargs):
        return baker.prepare(model, _fill_optional=True, *args, **kwargs)

    return factory
