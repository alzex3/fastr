import pytest
import random

from django.urls import reverse

from api.models import (
    Category, Attribute, Shop, Order, Product,
    ShippingNote, CartProduct, OrderShop,
)


@pytest.mark.django_db
class TestCategoryViewSet:
    def test_category_retrieve(self, anon_client, model_create):
        category = model_create(Category)
        category_attrs = {'id': category.id, 'name': category.name}

        url = reverse('api:categories-detail', kwargs={'pk': category.id})
        resp = anon_client.get(url)
        resp_category = resp.json()

        assert resp.status_code == 200
        assert resp_category == category_attrs

    def test_categories_list(self, anon_client, model_create):
        categories = model_create(Category, _quantity=3)
        categories_attrs = [{'id': category.id, 'name': category.name} for category in categories]

        url = reverse('api:categories-list')
        resp = anon_client.get(url)
        resp_categories = resp.json()

        assert resp.status_code == 200
        assert resp_categories == categories_attrs


@pytest.mark.django_db
class TestShippingNoteView:
    @staticmethod
    def _shipping_note_dict(shipping_note):
        return {
            'id': shipping_note.id,
            'country': shipping_note.country,
            'city': shipping_note.city,
            'street': shipping_note.street,
            'house': shipping_note.house,
            'building': shipping_note.building,
            'office': shipping_note.office,
            'phone': shipping_note.phone,
        }

    def test_shipping_note_create(self, buyer_user, buyer_client, model_prepare):
        shipping_note = model_prepare(ShippingNote, user=buyer_user)
        shipping_note_attrs = self._shipping_note_dict(shipping_note)

        url = reverse('api:buyer-shipping-notes-list')
        resp = buyer_client.post(url, shipping_note_attrs)
        resp_shipping_note = resp.json()

        assert resp.status_code == 201
        shipping_note_attrs.update(id=resp_shipping_note['id'])
        assert resp_shipping_note == shipping_note_attrs
        assert ShippingNote.objects.get(**shipping_note_attrs)

    def test_shipping_note_retrieve(self, buyer_user, buyer_client, model_create):
        shipping_note = model_create(ShippingNote, user=buyer_user)
        shipping_note_attrs = self._shipping_note_dict(shipping_note)

        url = reverse('api:buyer-shipping-notes-detail', kwargs={'pk': shipping_note.id})
        resp = buyer_client.get(url)
        resp_shipping_note = resp.json()

        assert resp.status_code == 200
        assert resp_shipping_note == shipping_note_attrs

    def test_shipping_notes_list(self, buyer_user, buyer_client, model_create):
        shipping_notes = model_create(ShippingNote, user=buyer_user, _quantity=3)
        shipping_notes_attrs = [self._shipping_note_dict(shipping_note) for shipping_note in shipping_notes]

        url = reverse('api:buyer-shipping-notes-list')
        resp = buyer_client.get(url)
        resp_shipping_notes = resp.json()

        assert resp.status_code == 200
        assert resp_shipping_notes == shipping_notes_attrs


@pytest.mark.django_db
class TestAttributeViewSet:
    def test_attribute_create(self, seller_client, model_prepare):
        attribute = model_prepare(Attribute)
        attribute_attrs = {'name': attribute.name}

        url = reverse('api:attributes-list')
        resp = seller_client.post(url, attribute_attrs)
        resp_attribute = resp.json()

        assert resp.status_code == 201
        attribute_attrs.update(id=resp_attribute['id'])
        assert resp_attribute == attribute_attrs
        assert Attribute.objects.get(**attribute_attrs)

    def test_attribute_retrieve(self, seller_client, model_create):
        attribute = model_create(Attribute)
        attribute_attrs = {'id': attribute.id, 'name': attribute.name}

        url = reverse('api:attributes-detail', kwargs={'pk': attribute.id})
        resp = seller_client.get(url)
        resp_attribute = resp.json()

        assert resp.status_code == 200
        assert resp_attribute == attribute_attrs

    def test_attributes_list(self, seller_client, model_create):
        attributes = model_create(Attribute, _quantity=3)
        attributes_attrs = [{'id': attribute.id, 'name': attribute.name} for attribute in attributes]

        url = reverse('api:attributes-list')
        resp = seller_client.get(url)
        resp_attributes = resp.json()

        assert resp.status_code == 200
        assert resp_attributes == attributes_attrs


@pytest.mark.django_db
class TestProductCreateViewSet:
    @staticmethod
    def _product_dict(product, product_attributes):
        return {
            'id': product.id,
            'category': product.category.id,
            'sku': product.sku,
            'name': product.name,
            'description': product.description,
            'product_attributes': product_attributes,
            'stock_quantity': product.stock_quantity,
            'price': str(product.price),
        }

    def test_product_create(self, seller_user, seller_client, model_create, model_prepare):
        set_shop = model_create(Shop, user=seller_user)
        set_attributes = model_create(Attribute, _quantity=3)

        product = model_prepare(Product, shop=set_shop, _save_related=True)
        product_attributes = [
            {'id': attribute.id, 'value': str(random.randint(1, 1000))}
            for attribute in set_attributes
        ]
        product_attrs = self._product_dict(product, product_attributes)

        url = reverse('api:seller-products-list')
        resp = seller_client.post(url, product_attrs)
        resp_product = resp.json()

        assert resp.status_code == 201
        product_attrs.update(id=resp_product['id'])
        assert resp_product == product_attrs
        product_attrs.pop('product_attributes')
        assert Product.objects.get(**product_attrs)

    def test_product_retrieve(self, seller_user, seller_client, model_create):
        set_shop = model_create(Shop, user=seller_user)

        product = model_create(Product, shop=set_shop)
        product_attributes = [
            {'id': product_attribute.attribute.id, 'value': product_attribute.value}
            for product_attribute in product.product_attributes.all()
        ]
        product_attrs = self._product_dict(product, product_attributes)

        url = reverse('api:seller-products-detail', kwargs={'pk': product.id})
        resp = seller_client.get(url)
        resp_product = resp.json()

        assert resp.status_code == 200
        assert resp_product == product_attrs

    def test_product_update(self, seller_user, seller_client, model_create, model_prepare):
        set_shop = model_create(Shop, user=seller_user)
        product = model_create(Product, shop=set_shop)

        update_product = model_prepare(Product, shop=set_shop, _save_related=True)
        update_product_attributes = [
            {'id': product_attribute.attribute.id, 'value': str(random.randint(1, 1000))}
            for product_attribute in product.product_attributes.all()
        ]
        update_product_attrs = self._product_dict(update_product, update_product_attributes)

        url = reverse('api:seller-products-detail', kwargs={'pk': product.id})
        resp = seller_client.patch(url, update_product_attrs)
        resp_product = resp.json()

        assert resp.status_code == 200
        update_product_attrs.update(id=resp_product['id'])
        assert resp_product == update_product_attrs
        update_product_attrs.pop('product_attributes')
        assert Product.objects.get(**update_product_attrs)

    def test_products_list(self, seller_user, seller_client, model_create):
        set_shop = model_create(Shop, user=seller_user)
        products = model_create(Product, shop=set_shop, _quantity=3)

        products_attrs = []
        for product in products:
            product_attributes = [
                {'id': product_attribute.attribute.id, 'value': product_attribute.value}
                for product_attribute in product.product_attributes.all()
            ]
            products_attrs.append(self._product_dict(product, product_attributes))

        url = reverse('api:seller-products-list')
        resp = seller_client.get(url)
        resp_products = resp.json()

        assert resp.status_code == 200
        assert resp_products == products_attrs


@pytest.mark.django_db
class TestProductRetrieveViewSet:
    @staticmethod
    def _product_dict(product, product_attributes):
        return {
            'id': product.id,
            'category': product.category.name,
            'sku': product.sku,
            'name': product.name,
            'shop': product.shop.name,
            'description': product.description,
            'product_attributes': product_attributes,
            'stock_quantity': product.stock_quantity,
            'price': str(product.price),
        }

    def test_product_retrieve(self, buyer_client, model_create):
        product = model_create(Product)
        product_attributes = [
            {
                'id': product_attribute.attribute.id,
                'name': product_attribute.attribute.name,
                'value': product_attribute.value
            }
            for product_attribute in product.product_attributes.all()
        ]
        product_attrs = self._product_dict(product, product_attributes)

        url = reverse('api:products-detail', kwargs={'pk': product.id})
        resp = buyer_client.get(url)
        resp_product = resp.json()

        assert resp.status_code == 200
        assert resp_product == product_attrs

    def test_products_list(self, buyer_client, model_create):
        products = model_create(Product, _quantity=3)
        products_attrs = []
        for product in products:
            product_attributes = [
                {
                    'id': product_attribute.attribute.id,
                    'name': product_attribute.attribute.name,
                    'value': product_attribute.value
                }
                for product_attribute in product.product_attributes.all()
            ]
            products_attrs.append(self._product_dict(product, product_attributes))

        url = reverse('api:products-list')
        resp = buyer_client.get(url)
        resp_products = resp.json()

        assert resp.status_code == 200
        assert resp_products == products_attrs


@pytest.mark.django_db
class TestShopCreateView:
    def test_seller_shop_create(self, seller_user, seller_client, model_create, model_prepare):
        set_categories = model_create(Category, _quantity=5)
        shop = model_prepare(Shop)
        shop_attrs = {
            'name': shop.name,
            'categories': [category.id for category in set_categories],
            'is_open': random.choice((True, False)),
        }

        url = reverse('api:seller-shop')
        resp = seller_client.post(url, shop_attrs)
        resp_shop = resp.json()

        assert resp.status_code == 201
        shop_attrs.update(id=resp_shop['id'])
        assert resp_shop == shop_attrs
        assert Shop.objects.get(user=seller_user, name=shop_attrs['name'])

    def test_seller_shop_retrieve(self, seller_user, seller_client, model_create):
        shop = model_create(Shop, user=seller_user)
        shop_attrs = {
            'id': shop.id,
            'name': shop.name,
            'categories': [category.id for category in shop.categories.all()],
            'is_open': shop.is_open,
        }

        url = reverse('api:seller-shop')
        resp = seller_client.get(url)
        resp_shop = resp.json()

        assert resp.status_code == 200
        assert resp_shop == shop_attrs


@pytest.mark.django_db
class TestShopRetrieveViewSet:
    def test_shop_retrieve(self, anon_client, model_create):
        shop = model_create(Shop)
        shop_attrs = {
            'id': shop.id,
            'name': shop.name,
            'categories': [category.name for category in shop.categories.all()],
        }

        url = reverse('api:shops-detail', kwargs={'pk': shop.id})
        resp = anon_client.get(url)
        resp_shop = resp.json()

        assert resp.status_code == 200
        assert resp_shop == shop_attrs

    def test_shops_list(self, anon_client, model_create):
        shops = model_create(Shop, _quantity=3)
        shops_attrs = []
        for shop in shops:
            shops_attrs.append({
                'id': shop.id,
                'name': shop.name,
                'categories': [category.name for category in shop.categories.all()],
            })

        url = reverse('api:shops-list')
        resp = anon_client.get(url)
        resp_shops = resp.json()

        assert resp.status_code == 200
        assert resp_shops == shops_attrs


@pytest.mark.django_db
class TestCartProductView:
    @staticmethod
    def _cart_products_dict(buyer_cart):
        total_sum = 0
        positions = []
        for cart_product in CartProduct.objects.filter(cart=buyer_cart):
            positions.append({
                'product': {
                    'id': cart_product.product.id,
                    'name': cart_product.product.name,
                    'shop': cart_product.product.shop.name,
                },
                'price': str(cart_product.product.price),
                'quantity': cart_product.quantity,
                'sum': str(cart_product.sum),
            })
            total_sum += cart_product.sum
        return {'positions': positions, 'total_sum': str(total_sum)}

    def test_cart_product_create(self, buyer_user, buyer_client, model_create):
        set_products = model_create(Product, stock_quantity=1000, _quantity=3)
        cart_products_attrs = [
            {'product': product.id, 'quantity': random.randint(1, 999)}
            for product in set_products
        ]

        url = reverse('api:buyer-cart')
        resp = buyer_client.post(url, cart_products_attrs)
        resp_cart_products = resp.json()

        assert resp.status_code == 201
        assert resp_cart_products == cart_products_attrs
        for cart_product_attr in resp_cart_products:
            assert CartProduct.objects.get(cart=buyer_user.cart, **cart_product_attr)

    def test_cart_product_update(self, buyer_user, buyer_client, model_create):
        cart_products = model_create(CartProduct, cart=buyer_user.cart, product__stock_quantity=1000, _quantity=3)
        update_cart_products_attrs = [
            {'product': cart_product.product.id, 'quantity': random.randint(1, 999)}
            for cart_product in cart_products
        ]

        url = reverse('api:buyer-cart')
        resp = buyer_client.patch(url, update_cart_products_attrs)
        resp_cart_products = resp.json()

        assert resp.status_code == 200
        assert resp_cart_products == update_cart_products_attrs
        for cart_product_attr in resp_cart_products:
            assert CartProduct.objects.get(cart=buyer_user.cart, **cart_product_attr)

    def test_cart_product_destroy(self, buyer_user, buyer_client, model_create):
        cart_products = model_create(CartProduct, cart=buyer_user.cart, _quantity=3)
        delete_cart_products = {
            'products': [cart_product.product.id for cart_product in cart_products],
        }

        url = reverse('api:buyer-cart')
        resp = buyer_client.delete(url, delete_cart_products)

        assert resp.status_code == 204
        for product in delete_cart_products['products']:
            assert not CartProduct.objects.filter(cart=buyer_user.cart, product=product)

    def test_cart_products_list(self, buyer_user, buyer_client, model_create):
        model_create(CartProduct, cart=buyer_user.cart, _quantity=3)
        cart_products_attrs = self._cart_products_dict(buyer_user.cart)

        url = reverse('api:buyer-cart')
        resp = buyer_client.get(url)
        resp_cart_products = resp.json()

        assert resp.status_code == 200
        assert resp_cart_products == cart_products_attrs


@pytest.mark.django_db
class TestOrderViewSet:
    @staticmethod
    def _order_positions_dict(order):
        total_sum = 0
        positions = []
        for order_product in order.order_products.all():
            positions.append({
                'product': {
                    'id': order_product.product.id,
                    'name': order_product.product.name,
                    'shop': order_product.product.shop.name,
                },
                'sold_price': str(order_product.sold_price),
                'quantity': order_product.quantity,
                'sum': str(order_product.sum),
            })
            total_sum += order_product.sum
        return {'positions': positions, 'total_sum': total_sum}

    def _order_dict(self, order):
        order_positions = self._order_positions_dict(order)
        order_shop_dict = {
            'order': order.id,
            'positions': order_positions['positions'],
            'statuses': [
                {'shop': order_shop.shop.name, 'status': order_shop.status}
                for order_shop in order.order_shops.all()
            ],
            'shipping_note': {
                'id': order.shipping_note.id,
                'country': order.shipping_note.country,
                'city': order.shipping_note.city,
                'street': order.shipping_note.street,
                'house': order.shipping_note.house,
                'building': order.shipping_note.building,
                'office': order.shipping_note.office,
                'phone': order.shipping_note.phone,
            },
            'total_sum': str(order_positions['total_sum']),
            'created_at': order.created_at.strftime('%d.%m.%Y')
        }
        return order_shop_dict

    def test_order_create(self, buyer_user, buyer_client, model_create, model_prepare, settings):
        set_cart_products = model_create(CartProduct, cart=buyer_user.cart, _quantity=3)
        set_shipping_note = model_create(ShippingNote, user=buyer_user)
        order_attrs = {'shipping_note': set_shipping_note.id}

        settings.EMAIL_ORDER_NOTIFICATIONS = False

        url = reverse('api:buyer-orders-list')
        resp = buyer_client.post(url, data=order_attrs)
        resp_order = resp.json()

        assert resp.status_code == 201
        order_attrs.update(order=resp_order['order'])
        assert resp_order == order_attrs
        order = Order.objects.get(
            id=resp_order['order'],
            user=buyer_user,
            shipping_note=set_shipping_note,
        )
        assert order

        for cart_product in set_cart_products:
            order_product_attrs = {
                'order': order,
                'product': cart_product.product,
                'quantity': cart_product.quantity,
                'sold_price': cart_product.product.price,
            }
            assert order.order_products.get(**order_product_attrs)

    def test_order_retrieve(self, buyer_user, buyer_client, model_create):
        order = model_create(Order, user=buyer_user)
        order_attrs = self._order_dict(order)

        url = reverse('api:buyer-orders-detail', kwargs={'pk': order.id})
        resp = buyer_client.get(url)
        resp_order = resp.json()

        assert resp.status_code == 200
        assert resp_order == order_attrs

    def test_orders_list(self, buyer_user, buyer_client, model_create):
        orders = model_create(Order, user=buyer_user, _quantity=3)
        orders_attrs = [self._order_dict(order) for order in orders]

        url = reverse('api:buyer-orders-list')
        resp = buyer_client.get(url)
        resp_orders = resp.json()

        assert resp.status_code == 200
        assert resp_orders == orders_attrs


@pytest.mark.django_db
class TestOrderShopViewSet:
    @staticmethod
    def _set_cart_products(set_products, buyer_user, model_create):
        set_cart_products = []
        for product in set_products:
            set_cart_products.append(
                model_create(CartProduct, cart=buyer_user.cart, product=product)
            )
        return set_cart_products

    @staticmethod
    def _order_positions_dict(order, set_shop):
        total_sum = 0
        positions = []
        for order_product in order.order_products.filter(product__shop=set_shop):
            positions.append({
                'product': order_product.product.id,
                'sold_price': str(order_product.sold_price),
                'quantity': order_product.quantity,
                'sum': str(order_product.sum),
            })
            total_sum += order_product.sum
        return {'positions': positions, 'total_sum': total_sum}

    def _order_shop_dict(self, order, set_shop):
        order_positions = self._order_positions_dict(order, set_shop)
        order_shop_dict = {
            'order': {
                'id': order.id,
                'positions': order_positions['positions'],
                'shipping_note': {
                    'id': order.shipping_note.id,
                    'country': order.shipping_note.country,
                    'city': order.shipping_note.city,
                    'street': order.shipping_note.street,
                    'house': order.shipping_note.house,
                    'building': order.shipping_note.building,
                    'office': order.shipping_note.office,
                    'phone': order.shipping_note.phone,
                    },
                'total_sum': str(order_positions['total_sum']),
                'created_at': order.created_at.strftime('%d.%m.%Y')
            },
            'status': order.order_shops.get(shop=set_shop, order=order.id).status,
        }
        return order_shop_dict

    def test_order_shop_retrieve(self, buyer_user, seller_user, seller_client, model_create):
        set_shop = model_create(Shop, user=seller_user)
        set_products = model_create(Product, shop=set_shop, _quantity=3)
        self._set_cart_products(set_products, buyer_user, model_create)

        order = model_create(Order, user=buyer_user)
        order_shop_attrs = self._order_shop_dict(order, set_shop)

        url = reverse('api:seller-orders-detail', kwargs={'order': order.id})
        resp = seller_client.get(url)
        resp_order_shop = resp.json()

        assert resp.status_code == 200
        assert resp_order_shop == order_shop_attrs

    def test_order_shop_update(self, buyer_user, seller_user, seller_client, model_create, settings):
        set_shop = model_create(Shop, user=seller_user)
        set_products = model_create(Product, shop=set_shop, _quantity=3)
        self._set_cart_products(set_products, buyer_user, model_create)
        settings.EMAIL_ORDER_NOTIFICATIONS = False

        order = model_create(Order, user=buyer_user)
        order_shop_attrs = self._order_shop_dict(order, set_shop)
        update_order_shop_attrs = {'status': 'confirmed'}

        url = reverse('api:seller-orders-detail', kwargs={'order': order.id})
        resp = seller_client.patch(url, update_order_shop_attrs)
        resp_order_shop = resp.json()

        assert resp.status_code == 200
        order_shop_attrs.update(**update_order_shop_attrs)
        assert resp_order_shop == order_shop_attrs
        assert OrderShop.objects.get(
            shop=set_shop,
            order=resp_order_shop['order']['id'],
            status=resp_order_shop['status'],
        )

    def test_orders_shop_list(self, buyer_user, seller_user, seller_client, model_create):
        set_shop = model_create(Shop, user=seller_user)

        orders_shop_attrs = []
        for i in range(3):
            set_products = model_create(Product, shop=set_shop, _quantity=3)
            self._set_cart_products(set_products, buyer_user, model_create)
            order = model_create(Order, user=buyer_user)
            orders_shop_attrs.append(self._order_shop_dict(order, set_shop))

        url = reverse('api:seller-orders-list')
        resp = seller_client.get(url)
        resp_orders_shop = resp.json()

        assert resp.status_code == 200
        assert resp_orders_shop == orders_shop_attrs
