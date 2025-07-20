from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductListView, ProductDetailView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='admin-category')
router.register(r'products', ProductViewSet, basename='admin-product')

urlpatterns = [
    path('admin/', include(router.urls)),
    path('products/', ProductListView.as_view(), name='public-product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='public-product-detail'),
]