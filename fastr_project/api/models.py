from django.db import models
from django.core import validators
from django.db.models import F, Sum

from users.models import User


ORDER_STATUS_CHOICES = (
    ('new', 'New'),
    ('confirmed', 'Confirmed'),
    ('assembled', 'Assembled'),
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('canceled', 'Canceled'),
)


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name', unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Сategories'

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=30, verbose_name='Name', unique=True)

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'

    def __str__(self):
        return self.name


class Shop(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='User',
        related_name='shop',
        on_delete=models.CASCADE,
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name='Сategories',
        related_name='shops',
    )
    name = models.CharField(max_length=50, verbose_name='Name', unique=True)
    is_open = models.BooleanField(verbose_name='Shop open', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'


class ShippingNote(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        related_name='shipping_notes',
        on_delete=models.CASCADE,
    )
    country = models.CharField(max_length=50, verbose_name='Country')
    city = models.CharField(max_length=70, verbose_name='City')
    street = models.CharField(max_length=100, verbose_name='Street')
    house = models.CharField(max_length=15, verbose_name='House', blank=True)
    building = models.CharField(max_length=15, verbose_name='Building', blank=True)
    office = models.CharField(max_length=15, verbose_name='Office', blank=True)
    phone = models.CharField(max_length=30, verbose_name='Phone')

    class Meta:
        verbose_name = 'Shipping note'
        verbose_name_plural = 'Shipping notes'

    def __str__(self):
        return f'{self.city}_{self.street}_{self.house}'


class Product(models.Model):
    shop = models.ForeignKey(
        Shop,
        verbose_name='Shop',
        related_name='products',
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Category',
        related_name='products',
        on_delete=models.CASCADE,
    )
    attributes = models.ManyToManyField(
        Attribute,
        verbose_name='Attributes',
        related_name='products',
        through='ProductAttribute',
    )
    sku = models.CharField(max_length=25, verbose_name='SKU')
    name = models.CharField(max_length=150, verbose_name='Name')
    description = models.CharField(max_length=500, verbose_name='Description')
    stock_quantity = models.PositiveSmallIntegerField(
        verbose_name='Stock quantity',
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(32000)],
    )
    price = models.DecimalField(
        verbose_name='Sold price',
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(99999999),
        ],
    )
    created_at = models.DateTimeField(verbose_name='Created date', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Update date', auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        constraints = [
            models.UniqueConstraint(fields=['shop', 'name'], name='unique_position')
        ]

    def __str__(self):
        return f'{self.name}'


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='Product',
        related_name='product_attributes',
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(
        Attribute,
        verbose_name='Attribute',
        related_name='product_attributes',
        on_delete=models.CASCADE,
    )
    value = models.CharField(verbose_name='Value', max_length=100)

    class Meta:
        unique_together = ('product', 'attribute')
        constraints = [
            models.UniqueConstraint(fields=['product', 'attribute'], name='unique_attributes')
        ]


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='User',
        related_name='cart',
        on_delete=models.CASCADE,

    )
    products = models.ManyToManyField(
        Product,
        verbose_name='Products',
        related_name='carts',
        through='CartProduct',
    )

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f'{self.user.email}_cart'


class CartProductManager(models.Manager):
    def get_queryset(self):
        return super(CartProductManager, self).get_queryset().annotate(
            sum=Sum(F('quantity') * F('product__price'))
        )


class CartProduct(models.Model):
    cart = models.ForeignKey(
        Cart,
        verbose_name='Cart',
        related_name='cart_products',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Product',
        related_name='cart_products',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Quantity',
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(999)],
    )
    objects = CartProductManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_positions')
        ]


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        related_name='orders',
        on_delete=models.CASCADE,
    )
    products = models.ManyToManyField(
        Product,
        verbose_name='Products',
        related_name='orders',
        through='OrderProduct',
    )
    shipping_note = models.ForeignKey(
        ShippingNote,
        verbose_name='Shipping note',
        related_name='orders',
        on_delete=models.CASCADE,
    )
    shops = models.ManyToManyField(
        Shop,
        verbose_name='Shops',
        related_name='orders',
        through='OrderShop',
    )
    created_at = models.DateTimeField(verbose_name='Created date', auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        cart_products = CartProduct.objects.filter(
            cart=self.user.cart
        )

        order_shops = []
        for position in cart_products:
            OrderProduct.objects.create(
                order=self,
                product=position.product,
                quantity=position.quantity,
                sold_price=position.product.price,
            )
            order_shops.append(position.product.shop)

        cart_products.delete()

        unic_order_shops = set(order_shops)
        for shop in unic_order_shops:
            OrderShop.objects.create(
                order=self,
                shop=shop,
                status='new',
            )

    def __str__(self):
        return f'order_{self.id}'


class OrderShop(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Order',
        related_name='order_shops',
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Shop',
        related_name='order_shops',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        verbose_name='Status',
        choices=ORDER_STATUS_CHOICES,
        max_length=9,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'shop'], name='unique_orders')
        ]


class OrderProductManager(models.Manager):
    def get_queryset(self):
        return super(OrderProductManager, self).get_queryset().annotate(
            sum=Sum(F('quantity') * F('sold_price'))
        )


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Order',
        related_name='order_products',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Product',
        related_name='order_products',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Quantity',
    )
    sold_price = models.DecimalField(
        verbose_name='Sold price',
        max_digits=10,
        decimal_places=2,
    )
    objects = OrderProductManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_positions')
        ]
