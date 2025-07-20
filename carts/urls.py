from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, OrderCreateView


cart_router = DefaultRouter()
cart_router.register(r'cart', CartViewSet, basename='cart')

order_router = DefaultRouter()
order_router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Dedicated path for creating an order.
    # This must come BEFORE the router's include.
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('', include(cart_router.urls)),
    path('', include(order_router.urls)),
]