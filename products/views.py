from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .filters import ProductFilter



# A ViewSet for Categories, accessible only to admin users
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Admin-only ViewSet for managing Categories.
    - list: GET /api/admin/categories/
    - create: POST /api/admin/categories/
    - retrieve: GET /api/admin/categories/{id}/
    - update: PUT /api/admin/categories/{id}/
    - partial_update: PATCH /api/admin/categories/{id}/
    - destroy: DELETE /api/admin/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]



# A ViewSet for Products, accessible only to admin users
class ProductViewSet(viewsets.ModelViewSet):
    """
    Admin-only ViewSet for managing Products.
    - list: GET /api/admin/products/
    - create: POST /api/admin/products/
    - retrieve: GET /api/admin/products/{id}/
    - update: PUT /api/admin/products/{id}/
    - partial_update: PATCH /api/admin/products/{id}/
    - destroy: DELETE /api/admin/products/{id}/
    """
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    # Customizing the destroy method to return a 200 status with a custom message
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Product successfully deleted."},
            status=status.HTTP_200_OK
        )



# Generic API views for listing and retrieving products to be used by all users

class ProductListView(generics.ListAPIView):
    """
    Public API view to list all available products.
    Supports filtering and pagination.
    - list: GET /api/products/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.select_related('category').all().order_by('id')

    #overriding the list method to message if no products are found
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(
                {"detail": "No products found matching your criteria."},
                status=status.HTTP_404_NOT_FOUND
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    """
    Public API view to retrieve a single product by its ID.
    - retrieve: GET /api/products/{id}/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').all()