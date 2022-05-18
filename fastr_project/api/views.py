from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import viewsets, status, mixins

from api import serializers
from api.permissions import IsBuyer, IsSeller, IsSellerHasShop, IsSellerHasNoShop
from api.models import Category, Attribute, Shop, ShippingNote, Product, Order, CartProduct, OrderShop, OrderProduct


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (AllowAny,)


class ShippingNoteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.ShippingNoteSerializer
    permission_classes = (IsBuyer,)

    def get_queryset(self):
        return ShippingNote.objects.filter(user=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AttributeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer
    permission_classes = (IsSeller,)


class ProductCreateViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.ProductCreateSerializer
    permission_classes = (IsSeller, IsSellerHasShop)

    def get_queryset(self):
        return Product.objects.filter(shop=self.request.user.shop)

    def perform_create(self, serializer):
        serializer.save(shop=self.request.user.shop)


class ProductRetrieveViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(shop__is_open=True)
    serializer_class = serializers.ProductRetrieveSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', 'description')


class ShopCreateView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericAPIView,
):
    serializer_class = serializers.ShopCreateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsSeller, IsSellerHasNoShop)
        else:
            self.permission_classes = (IsSeller, IsSellerHasShop)

        return super(ShopCreateView, self).get_permissions()

    def get_object(self):
        return self.request.user.shop

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ShopRetrieveViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Shop.objects.filter(is_open=True)
    serializer_class = serializers.ShopRetrieveSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class CartView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericAPIView,
):
    permission_classes = (IsBuyer,)

    def get_object(self):
        return self.request.user.cart

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())

        if self.request.method == 'GET':
            return serializers.CartRetrieveSerializer(*args, **kwargs)

        return serializers.CartProductCreateSerializer(many=True, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(cart=self.request.user.cart)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        cart = self.get_object()
        delete_products = request.data.get('products')

        if delete_products:
            for product in delete_products:
                cart_product = CartProduct.objects.filter(cart=cart, product=product)

                if cart_product:
                    cart_product.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'products': ['Required field, not be empty.']},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = (IsBuyer,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.OrderCreateSerializer
        return serializers.OrderRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderShopViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.OrderShopRetrieveSerializer
    lookup_field = 'order'
    permission_classes = (IsSeller, IsSellerHasShop)

    def get_queryset(self):
        shop = self.request.user.shop

        prefetch_positions = Prefetch(
            'order__order_products',
            OrderProduct.objects.filter(product__shop=shop)
        )

        return OrderShop.objects.filter(shop=shop).prefetch_related(prefetch_positions)
