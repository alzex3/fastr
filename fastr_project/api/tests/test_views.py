import pytest
import random

from django.urls import reverse

from api.models import (
    Category, Attribute, Shop, Order, Product,
    ShippingNote, CartProduct, OrderShop, OrderProduct, ProductAttribute
)


@pytest.mark.django_db(reset_sequences=True)
class TestCategoryViewSet:
    def test_category_retrieve(self, anon_client, model_create):
        category = model_create(Category)
        category_attrs = {'id': category.id, 'name': category.name}

        url = reverse('api:categories-detail', kwargs={'pk': category.id})
        resp = anon_client.get(url)
        resp_category = resp.json()

        assert resp.status_code == 200
        assert category_attrs == resp_category

    def test_categories_list(self, anon_client, model_create):
        categories = model_create(Category, _quantity=3)
        categories_attrs = [{'id': category.id, 'name': category.name} for category in categories]

        url = reverse('api:categories-list')
        resp = anon_client.get(url)
        resp_categories = resp.json()

        assert resp.status_code == 200
        assert categories_attrs == resp_categories


@pytest.mark.django_db(reset_sequences=True)
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
        assert shipping_note_attrs == resp_shipping_note
        assert ShippingNote.objects.get(**shipping_note_attrs)

    def test_shipping_note_retrieve(self, buyer_user, buyer_client, model_create):
        shipping_note = model_create(ShippingNote, user=buyer_user)
        shipping_note_attrs = self._shipping_note_dict(shipping_note)

        url = reverse('api:buyer-shipping-notes-detail', kwargs={'pk': shipping_note.id})
        resp = buyer_client.get(url)
        resp_shipping_note = resp.json()

        assert resp.status_code == 200
        assert shipping_note_attrs == resp_shipping_note

    def test_shipping_notes_list(self, buyer_user, buyer_client, model_create):
        shipping_notes = model_create(ShippingNote, user=buyer_user, _quantity=3)
        shipping_notes_attrs = [self._shipping_note_dict(shipping_note) for shipping_note in shipping_notes]

        url = reverse('api:buyer-shipping-notes-list')
        resp = buyer_client.get(url)
        resp_shipping_notes = resp.json()

        assert resp.status_code == 200
        assert shipping_notes_attrs == resp_shipping_notes


@pytest.mark.django_db(reset_sequences=True)
class TestAttributeViewSet:
    def test_attribute_create(self, seller_client, model_prepare):
        attribute = model_prepare(Attribute)
        attribute_attrs = {'id': attribute.id, 'name': attribute.name}

        url = reverse('api:attributes-list')
        resp = seller_client.post(url, attribute_attrs)
        resp_attribute = resp.json()

        assert resp.status_code == 201
        attribute_attrs.update(id=resp_attribute['id'])
        assert attribute_attrs == resp_attribute
        assert Attribute.objects.get(**attribute_attrs)

    def test_attribute_retrieve(self, seller_client, model_create):
        attribute = model_create(Attribute)
        attribute_attrs = {'id': attribute.id, 'name': attribute.name}

        url = reverse('api:attributes-detail', kwargs={'pk': attribute.id})
        resp = seller_client.get(url)
        resp_attribute = resp.json()

        assert resp.status_code == 200
        assert attribute_attrs == resp_attribute

    def test_attributes_list(self, seller_client, model_create):
        attributes = model_create(Attribute, _quantity=3)
        attributes_attrs = [{'id': attribute.id, 'name': attribute.name} for attribute in attributes]

        url = reverse('api:attributes-list')
        resp = seller_client.get(url)
        resp_attributes = resp.json()

        assert resp.status_code == 200
        assert attributes_attrs == resp_attributes


@pytest.mark.django_db(reset_sequences=True)
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
        assert product_attrs == resp_product
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
        assert product_attrs == resp_product

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
        assert update_product_attrs == resp_product
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
        assert products_attrs == resp_products


@pytest.mark.django_db(reset_sequences=True)
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
        assert product_attrs == resp_product

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
        assert products_attrs == resp_products


@pytest.mark.django_db(reset_sequences=True)
class TestShopCreateView:
    def test_seller_shop_create(self, seller_user, seller_client, model_create):
        set_categories = model_create(Category, _quantity=5)

        shop_attrs = {
            'name': 'iStore',
            'categories': [category.id for category in set_categories],
        }

        url = reverse('api:seller-shop')
        resp = seller_client.post(url, shop_attrs)
        resp_shop = resp.json()

        assert resp.status_code == 201

        for attr, value in shop_attrs.items():
            assert value == resp_shop[attr]

        assert Shop.objects.get(user=seller_user, name=shop_attrs['name'])

    def test_seller_shop_retrieve(self, seller_user, seller_client, model_create):
        set_categories = model_create(Category, _quantity=5)
        shop = model_create(Shop, user=seller_user, categories=set_categories)

        url = reverse('api:seller-shop')
        resp = seller_client.get(url)
        resp_shop = resp.json()

        assert resp.status_code == 200
        assert resp_shop['name'] == shop.name

        for category in shop.categories.all():
            assert category.id in resp_shop['categories']


@pytest.mark.django_db(reset_sequences=True)
class TestShopRetrieveViewSet:
    def test_shop_retrieve(self, anon_client, model_create):
        set_categories = model_create(Category, _quantity=5)
        shop = model_create(Shop, categories=set_categories)

        url = reverse('api:shops-detail', kwargs={'pk': shop.id})
        resp = anon_client.get(url)
        resp_shop = resp.json()

        assert resp.status_code == 200
        assert resp_shop['name'] == shop.name

        for category in shop.categories.all():
            assert category.name in resp_shop['categories']

    def test_shops_list(self, anon_client, model_create):
        set_categories = model_create(Category, _quantity=5)
        shops = model_create(Shop, categories=set_categories, _quantity=3)

        url = reverse('api:shops-list')
        resp = anon_client.get(url)
        resp_shops = resp.json()

        assert resp.status_code == 200

        for i, resp_shop in enumerate(resp_shops):
            assert resp_shop['name'] == shops[i].name

            for category in shops[i].categories.all():
                assert category.name in resp_shop['categories']


@pytest.mark.django_db(reset_sequences=True)
class TestCartProductView:
    def test_cart_product_create(self, buyer_client, model_create):
        model_create(Product, stock_quantity=random.randint(5, 1000), _quantity=3)

        cart_products_attrs = [
            {
                'product': 1,
                'quantity': 2,
            },
            {
                'product': 2,
                'quantity': 23,
            },
        ]

        url = reverse('api:buyer-cart')
        resp = buyer_client.post(url, cart_products_attrs)
        resp_cart_products = resp.json()

        assert resp.status_code == 201

        for cart_product_attrs in cart_products_attrs:
            assert cart_product_attrs in resp_cart_products
            assert CartProduct.objects.get(**cart_product_attrs)

    def test_cart_product_update(self, buyer_user, buyer_client, model_create):
        model_create(CartProduct, cart=buyer_user.cart, _quantity=3)

        cart_products_attrs = [
            {
                'product': 1,
                'quantity': 2,
            },
            {
                'product': 2,
                'quantity': 23,
            },
        ]

        url = reverse('api:buyer-cart')
        resp = buyer_client.patch(url, cart_products_attrs)
        resp_cart_products = resp.json()

        assert resp.status_code == 200

        for cart_product_attrs in cart_products_attrs:
            assert cart_product_attrs in resp_cart_products
            assert CartProduct.objects.get(**cart_product_attrs)

    def test_cart_product_destroy(self, buyer_user, buyer_client, model_create):
        model_create(CartProduct, cart=buyer_user.cart, _quantity=3)

        delete_cart_products = {
            'products': [1, 2],
        }

        url = reverse('api:buyer-cart')
        resp = buyer_client.delete(url, delete_cart_products)

        assert resp.status_code == 204

        for product_id in delete_cart_products['products']:
            assert not CartProduct.objects.filter(product__id=product_id)

    def test_cart_products_list(self, buyer_user, buyer_client, model_create):
        cart_products = model_create(CartProduct, cart=buyer_user.cart, _quantity=3)

        url = reverse('api:buyer-cart')
        resp = buyer_client.get(url)
        resp_cart_products = resp.json()

        assert resp.status_code == 200

        for i, resp_product in enumerate(resp_cart_products['positions']):
            assert resp_product['product']['id'] == cart_products[i].product.id
            assert resp_product['quantity'] == cart_products[i].quantity
            assert float(resp_product['price']) == float(cart_products[i].product.price)


@pytest.mark.django_db(reset_sequences=True)
class TestOrderViewSet:
    def test_order_create(self, buyer_user, buyer_client, model_create, settings):
        set_cart_products = model_create(CartProduct, cart=buyer_user.cart, _quantity=3)
        set_shipping_note = model_create(ShippingNote, user=buyer_user)

        settings.EMAIL_ORDER_NOTIFICATIONS = False

        order_attrs = {
            'shipping_note': set_shipping_note.id,
        }

        url = reverse('api:buyer-orders-list')
        resp = buyer_client.post(url, data=order_attrs)
        resp_order = resp.json()

        assert resp.status_code == 201

        assert resp_order['order']
        assert resp_order['shipping_note'] == set_shipping_note.id

        assert Order.objects.get(
            id=resp_order['order'],
            user=buyer_user,
            shipping_note=set_shipping_note,
        )

        order = Order.objects.get(id=resp_order['order'])
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

        url = reverse('api:buyer-orders-detail', kwargs={'pk': order.id})
        resp = buyer_client.get(url)
        resp_order = resp.json()

        assert resp.status_code == 200

        assert resp_order['order'] == order.id

        total_sum = 0
        for position in resp_order['positions']:
            order_product = OrderProduct.objects.get(
                order=resp_order['order'],
                quantity=position['quantity'],
                product__id=position['product']['id'],
                product__name=position['product']['name'],
                product__shop__name=position['product']['shop'],
            )

            assert order_product
            assert float(order_product.sold_price) == position['sold_price']
            assert float(order_product.sum) == position['sum']
            total_sum += order_product.sum

        for status in resp_order['statuses']:
            order_statuses = OrderShop.objects.get(
                order=resp_order['order'],
                shop__name=status['shop'],
                status=status['status'],
            )
            assert order_statuses

        order_shipping_note = ShippingNote.objects.get(
            id=resp_order['shipping_note']['id'],
            country=resp_order['shipping_note']['country'],
            city=resp_order['shipping_note']['city'],
            street=resp_order['shipping_note']['street'],
            house=resp_order['shipping_note']['house'],
            building=resp_order['shipping_note']['building'],
            office=resp_order['shipping_note']['office'],
            phone=resp_order['shipping_note']['phone'],
        )
        assert order_shipping_note

        assert float(total_sum) == resp_order['total_sum']
        assert order.created_at.strftime('%d.%m.%Y') == resp_order['created_at']

    def test_orders_list(self, buyer_user, buyer_client, model_create):
        orders = model_create(Order, user=buyer_user, _quantity=3)

        url = reverse('api:buyer-orders-list')
        resp = buyer_client.get(url)
        resp_orders = resp.json()

        assert resp.status_code == 200

        for i, resp_order in enumerate(resp_orders):
            assert resp_order['order'] == orders[i].id

            total_sum = 0
            for position in resp_order['positions']:
                order_product = OrderProduct.objects.get(
                    order=resp_order['order'],
                    quantity=position['quantity'],
                    product__id=position['product']['id'],
                    product__name=position['product']['name'],
                    product__shop__name=position['product']['shop'],
                )

                assert order_product
                assert float(order_product.sold_price) == position['sold_price']
                assert float(order_product.sum) == position['sum']
                total_sum += order_product.sum

            for status in resp_order['statuses']:
                order_statuses = OrderShop.objects.get(
                    order=resp_order['order'],
                    shop__name=status['shop'],
                    status=status['status'],
                )
                assert order_statuses

            order_shipping_note = ShippingNote.objects.get(
                id=resp_order['shipping_note']['id'],
                country=resp_order['shipping_note']['country'],
                city=resp_order['shipping_note']['city'],
                street=resp_order['shipping_note']['street'],
                house=resp_order['shipping_note']['house'],
                building=resp_order['shipping_note']['building'],
                office=resp_order['shipping_note']['office'],
                phone=resp_order['shipping_note']['phone'],
            )
            assert order_shipping_note

            assert float(total_sum) == resp_order['total_sum']
            assert orders[i].created_at.strftime('%d.%m.%Y') == resp_order['created_at']


@pytest.mark.django_db(reset_sequences=True)
class TestOrderShopViewSet:
    def test_order_shop_retrieve(self, buyer_user, seller_user, seller_client, model_create):
        set_shop = model_create(Shop, user=seller_user)
        set_seller_products = model_create(Product, shop=set_shop, _quantity=3)
        set_products = model_create(Product, _quantity=3) + set_seller_products

        set_cart_products = []
        for product in set_products:
            set_cart_products.append(
                model_create(
                    CartProduct,
                    cart=buyer_user.cart,
                    product=product,
                )
            )

        order = model_create(Order, user=buyer_user)

        url = reverse('api:seller-orders-detail', kwargs={'order': order.id})
        resp = seller_client.get(url)
        resp_order = resp.json()

        assert resp.status_code == 200

        assert resp_order['order']['id'] == order.id

        total_sum = 0
        for position in resp_order['order']['positions']:
            order_product = OrderProduct.objects.get(
                order=resp_order['order']['id'],
                quantity=position['quantity'],
                product__id=position['product'],
            )

            assert order_product
            assert float(order_product.sold_price) == position['sold_price']
            assert float(order_product.sum) == position['sum']
            total_sum += order_product.sum

        order_shipping_note = ShippingNote.objects.get(
            id=resp_order['order']['shipping_note']['id'],
            country=resp_order['order']['shipping_note']['country'],
            city=resp_order['order']['shipping_note']['city'],
            street=resp_order['order']['shipping_note']['street'],
            house=resp_order['order']['shipping_note']['house'],
            building=resp_order['order']['shipping_note']['building'],
            office=resp_order['order']['shipping_note']['office'],
            phone=resp_order['order']['shipping_note']['phone'],
        )
        assert order_shipping_note

        assert float(total_sum) == resp_order['order']['total_sum']
        assert order.created_at.strftime('%d.%m.%Y') == resp_order['order']['created_at']

        assert OrderShop.objects.get(
            shop=set_shop,
            order=resp_order['order']['id'],
            status=resp_order['status'],
        )

    def test_order_shop_update(self, buyer_user, seller_user, seller_client, model_create, settings):
        set_shop = model_create(Shop, user=seller_user)
        set_seller_products = model_create(Product, shop=set_shop, _quantity=3)
        set_products = model_create(Product, _quantity=3) + set_seller_products

        set_cart_products = []
        for product in set_products:
            set_cart_products.append(
                model_create(
                    CartProduct,
                    cart=buyer_user.cart,
                    product=product,
                )
            )

        order = model_create(Order, user=buyer_user)

        settings.EMAIL_ORDER_NOTIFICATIONS = False

        order_shop_attr = {
            'status': 'confirmed',
        }

        url = reverse('api:seller-orders-detail', kwargs={'order': order.id})
        resp = seller_client.patch(url, order_shop_attr)
        resp_order = resp.json()

        assert resp.status_code == 200

        assert resp_order['order']['id'] == order.id

        total_sum = 0
        for position in resp_order['order']['positions']:
            order_product = OrderProduct.objects.get(
                order=resp_order['order']['id'],
                quantity=position['quantity'],
                product__id=position['product'],
            )

            assert order_product
            assert float(order_product.sold_price) == position['sold_price']
            assert float(order_product.sum) == position['sum']
            total_sum += order_product.sum

        order_shipping_note = ShippingNote.objects.get(
            id=resp_order['order']['shipping_note']['id'],
            country=resp_order['order']['shipping_note']['country'],
            city=resp_order['order']['shipping_note']['city'],
            street=resp_order['order']['shipping_note']['street'],
            house=resp_order['order']['shipping_note']['house'],
            building=resp_order['order']['shipping_note']['building'],
            office=resp_order['order']['shipping_note']['office'],
            phone=resp_order['order']['shipping_note']['phone'],
        )
        assert order_shipping_note

        assert float(total_sum) == resp_order['order']['total_sum']
        assert order.created_at.strftime('%d.%m.%Y') == resp_order['order']['created_at']

        assert order_shop_attr['status'] == resp_order['status']
        assert OrderShop.objects.get(
            shop=set_shop,
            order=resp_order['order']['id'],
            status=resp_order['status'],
        )

    def test_orders_shop_list(self, buyer_user, seller_user, seller_client, model_create):
        set_shop = model_create(Shop, user=seller_user)
        set_seller_products = model_create(Product, shop=set_shop, _quantity=3)
        set_products = model_create(Product, _quantity=3) + set_seller_products

        set_cart_products = []
        for product in set_products:
            set_cart_products.append(
                model_create(
                    CartProduct,
                    cart=buyer_user.cart,
                    product=product,
                )
            )

        orders = model_create(Order, user=buyer_user, _quantity=3)

        url = reverse('api:seller-orders-list')
        resp = seller_client.get(url)
        resp_orders = resp.json()

        assert resp.status_code == 200

        for i, resp_order in enumerate(resp_orders):

            assert resp_order['order']['id'] == orders[i].id

            total_sum = 0
            for position in resp_order['order']['positions']:
                order_product = OrderProduct.objects.get(
                    order=resp_order['order']['id'],
                    quantity=position['quantity'],
                    product__id=position['product'],
                )

                assert order_product
                assert float(order_product.sold_price) == position['sold_price']
                assert float(order_product.sum) == position['sum']
                total_sum += order_product.sum

            order_shipping_note = ShippingNote.objects.get(
                id=resp_order['order']['shipping_note']['id'],
                country=resp_order['order']['shipping_note']['country'],
                city=resp_order['order']['shipping_note']['city'],
                street=resp_order['order']['shipping_note']['street'],
                house=resp_order['order']['shipping_note']['house'],
                building=resp_order['order']['shipping_note']['building'],
                office=resp_order['order']['shipping_note']['office'],
                phone=resp_order['order']['shipping_note']['phone'],
            )
            assert order_shipping_note

            assert float(total_sum) == resp_order['order']['total_sum']
            assert orders[i].created_at.strftime('%d.%m.%Y') == resp_order['order']['created_at']

            assert OrderShop.objects.get(
                shop=set_shop,
                order=resp_order['order']['id'],
                status=resp_order['status'],
            )
