from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet, AttributeViewSet, ShopRetrieveViewSet,
    ShippingNoteViewSet, ProductRetrieveViewSet, OrderViewSet,
    ShopCreateView, ProductCreateViewSet, OrderShopViewSet, CartProductView
)


router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('attributes', AttributeViewSet)
router.register('products', ProductRetrieveViewSet)
router.register('shops', ShopRetrieveViewSet)

seller_router = DefaultRouter()
seller_router.register('orders', OrderShopViewSet, basename='seller-orders')
seller_router.register('products', ProductCreateViewSet, basename='seller-products')

buyer_router = DefaultRouter()
buyer_router.register('orders', OrderViewSet, basename='buyer-orders')
buyer_router.register('shipping-notes', ShippingNoteViewSet, basename='buyer-shipping-notes')


urlpatterns = [

    path('v1/', include(router.urls)),

    path('v1/seller/', include(seller_router.urls)),
    path('v1/seller/shop/', ShopCreateView.as_view()),

    path('v1/buyer/', include(buyer_router.urls)),
    path('v1/buyer/cart/', CartProductView.as_view()),

]
