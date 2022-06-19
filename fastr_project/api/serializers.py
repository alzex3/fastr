from django.db.models import Sum
from django.conf import settings

from rest_framework import serializers

from api.models import (
    Category, Attribute, Shop, ShippingNote, Product, Order,
    ProductAttribute, CartProduct, Cart, OrderProduct, OrderShop
)
from api.tasks import (
    order_created_email, order_received_email,
    order_updated_email
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ShippingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingNote
        fields = ('id', 'country', 'city', 'street', 'house', 'building', 'office', 'phone')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'shop')


class ProductCreateAttributesSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all(), source='attribute')

    class Meta:
        model = ProductAttribute
        fields = ('id', 'value')


class ProductCreateSerializer(serializers.ModelSerializer):
    product_attributes = ProductCreateAttributesSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'category', 'product_attributes', 'sku', 'name', 'description', 'stock_quantity', 'price')

    def validate(self, data):
        shop = self.context['request'].user.shop

        if data.get('name'):
            product_exists = Product.objects.filter(
                shop=shop, name=data['name']
            ).exists()

            if product_exists:
                raise serializers.ValidationError('Failed! Shop already have product with that name!')

        return data

    def create(self, validated_data):
        product_attributes = validated_data.pop('product_attributes')

        product = Product.objects.create(**validated_data)

        for product_attribute in product_attributes:
            ProductAttribute.objects.create(
                product=product,
                **product_attribute,
            )

        return product

    def update(self, product, validated_data):
        product_attributes = validated_data.pop('product_attributes', {})

        Product.objects.filter(id=product.id).update(**validated_data)
        updated_product = Product.objects.get(id=product.id)

        for product_attribute in product_attributes:
            if product_attribute.get('value') and product_attribute.get('attribute'):
                ProductAttribute.objects.update_or_create(
                    product=updated_product,
                    attribute=product_attribute['attribute'],
                    defaults={'value': product_attribute['value']}
                )

        return updated_product


class ProductRetrieveAttributesSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all(), source='attribute')
    name = serializers.StringRelatedField(source='attribute.name')

    class Meta:
        model = ProductAttribute
        fields = ('id', 'name', 'value')


class ProductRetrieveSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    product_attributes = ProductRetrieveAttributesSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            'id', 'shop', 'category', 'product_attributes', 'sku', 'name', 'description', 'stock_quantity', 'price'
        )


class ShopCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ('id', 'name', 'categories', 'is_open')


class ShopRetrieveSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Shop
        fields = ('id', 'name', 'categories')


class CartProductCreateListSerializer(serializers.ListSerializer):
    def update(self, cart, validated_data):

        result = []
        for position in validated_data:
            product = position.get('product')
            quantity = {'quantity': position.get('quantity')}

            cart_product = CartProduct.objects.filter(
                cart=cart,
                product=product
            ).first()

            if cart_product:
                result.append(self.child.update(cart_product, quantity))

        return result


class CartProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartProduct
        fields = ('product', 'quantity')
        list_serializer_class = CartProductCreateListSerializer

    def validate(self, data):
        request = self.context['request']

        product = data.get('product')
        if request.method == 'POST':
            cart = request.user.cart
            product = data.get('product')

            cart_product_exist = CartProduct.objects.filter(
                cart=cart, product=product
            ).exists()

            if cart_product_exist:
                raise serializers.ValidationError(
                    f'Failed! Cart already have product with id: {product.id}!'
                )

        quantity = data.get('quantity')
        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f'Failed! This quantity of product with id: {product.id}, not in stock!'
            )

        return data


class CartRetrievePositionsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    price = serializers.CharField(source='product.price')
    sum = serializers.CharField()

    class Meta:
        model = CartProduct
        fields = ('product', 'price', 'quantity', 'sum')


class CartRetrieveSerializer(serializers.ModelSerializer):
    positions = CartRetrievePositionsSerializer(source='cart_products', many=True)
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('positions', 'total_sum')

    @staticmethod
    def get_total_sum(obj: Cart) -> str:
        total_sum = obj.cart_products.aggregate(Sum('sum'))['sum__sum']
        if total_sum:
            return str(total_sum)
        return '0'


class OrderCreateSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(source='id', read_only=True)

    class Meta:
        model = Order
        fields = ('order', 'shipping_note')

    def validate(self, data):
        user = self.context['request'].user
        cart = self.context['request'].user.cart

        cart_products = CartProduct.objects.filter(cart=cart)
        if not cart_products:
            raise serializers.ValidationError(
                'Failed! You do not have any positions in cart!'
            )

        shipping_note = data.get('shipping_note')
        user_shipping_note_exist = ShippingNote.objects.filter(id=shipping_note.id, user=user).exists()
        if not user_shipping_note_exist:
            raise serializers.ValidationError(
                'Failed! You do not have shipping note with that id!'
            )

        return data

    def create(self, validated_data):
        created_order = super().create(validated_data)

        if settings.EMAIL_ORDER_NOTIFICATIONS:
            order_created_email.delay(created_order.id)
            order_received_email.delay(created_order.id)

        return created_order


class OrderRetrievePositionsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    sold_price = serializers.CharField
    sum = serializers.CharField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ('product', 'sold_price', 'quantity', 'sum')


class OrderRetrieveStatusesSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()

    class Meta:
        model = OrderShop
        fields = ('shop', 'status')


class OrderRetrieveSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    positions = OrderRetrievePositionsSerializer(source='order_products', many=True)
    statuses = OrderRetrieveStatusesSerializer(source='order_shops', many=True)
    shipping_note = ShippingNoteSerializer()
    total_sum = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField('%d.%m.%Y')

    class Meta:
        model = Order
        fields = ('order', 'positions', 'statuses', 'shipping_note', 'total_sum', 'created_at')

    @staticmethod
    def get_total_sum(obj: Order) -> str:
        return str(obj.order_products.aggregate(Sum('sum'))['sum__sum'])


class OrderShopRetrieveOrderPositionsSerializer(serializers.ModelSerializer):
    sold_price = serializers.CharField()
    sum = serializers.CharField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ('product', 'sold_price', 'quantity', 'sum')


class OrderShopRetrieveOrderSerializer(serializers.ModelSerializer):
    positions = OrderShopRetrieveOrderPositionsSerializer(source='order_products', many=True)
    shipping_note = ShippingNoteSerializer()
    total_sum = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField('%d.%m.%Y')

    class Meta:
        model = Order
        fields = ('id', 'positions', 'shipping_note', 'total_sum', 'created_at')

    @staticmethod
    def get_total_sum(obj: Order) -> str:
        return str(obj.order_products.aggregate(Sum('sum'))['sum__sum'])


class OrderShopRetrieveSerializer(serializers.ModelSerializer):
    order = OrderShopRetrieveOrderSerializer(read_only=True)

    class Meta:
        model = OrderShop
        fields = ('order', 'status')

    def update(self, order_shop, validated_data):
        updated_order_shop = super().update(order_shop, validated_data)

        if settings.EMAIL_ORDER_NOTIFICATIONS:
            order_updated_email.delay(updated_order_shop.id)

        return updated_order_shop
