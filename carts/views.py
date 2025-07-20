from django.db import transaction
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from products.models import Product

class CartViewSet(viewsets.ViewSet):
    """
    A ViewSet for viewing and managing the user's cart.
    - list: GET /api/cart/ (View your cart)
    - create: POST /api/cart/ (Add an item)
    - partial_update: PATCH /api/cart/{item_id}/ (Update item quantity)
    - destroy: DELETE /api/cart/{item_id}/ (Remove an item)
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Retrieves the authenticated user's cart.
        Creates a cart if one doesn't exist.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        """
        Add a product to the cart or update its quantity if it already exists.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            return Response(
                {"detail": "Quantity must be a positive number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not product_id:
            return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if quantity > product.stock:
            return Response({"detail": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
            
        if cart_item.quantity > product.stock:
            return Response({"detail": "Total quantity exceeds available stock."}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """
        Update the quantity of a specific item in the cart.
        """
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
             return Response({"detail": "You do not have a cart."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(id=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({"detail": "Quantity is required for an update."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                cart_item.delete()
                # Use a new CartSerializer to reflect the updated cart state after deletion
                serializer = CartSerializer(cart)
                return Response(
                    {"detail": "Cart item removed due to zero quantity.", "cart": serializer.data},
                    status=status.HTTP_200_OK
                )
        except (ValueError, TypeError):
            return Response({"detail": "Quantity must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)
            
        if quantity > cart_item.product.stock:
            return Response({"detail": "Quantity exceeds available stock."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        # Return the entire cart state so the frontend can update totals
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Remove an item from the cart entirely.
        """
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "You do not have a cart."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(id=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        
        return Response(
            {"detail": "Item removed from cart successfully."}, 
            status=status.HTTP_200_OK
        )


# === ORDER VIEWS ===

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only ViewSet for users to view their orders.
    Also allows a user to cancel a 'Pending' order.
    - list: GET /api/orders/ (View your order history)
    - retrieve: GET /api/orders/{id}/ (View a specific order)
    - cancel: POST /api/orders/{id}/cancel/ (Cancel a pending order)
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the orders
        for the currently authenticated user.
        """
        return Order.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Custom list method to add a message for users with no orders.
        """
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "You have not placed any orders yet."},
                status=status.HTTP_200_OK
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Allows a user to cancel their own order if it is still pending.
        """
        order = self.get_object()
        
        if order.status != Order.OrderStatus.PENDING:
            return Response(
                {"detail": "This order can no longer be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            order.status = Order.OrderStatus.CANCELLED
            order.save()

            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()

        serializer = self.get_serializer(order)
        return Response(
            {"detail": "Order has been successfully cancelled.", "order": serializer.data},
            status=status.HTTP_200_OK
        )

class OrderCreateView(generics.GenericAPIView):
    """
    An API view to create an order from the user's cart.
    - post: POST /api/orders/create/ (Places an order)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            raise ValidationError("You do not have a cart.")

        if cart.items.count() == 0:
            raise ValidationError("Your cart is empty. Cannot place an order.")

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    total_price=sum(item.total_price for item in cart.items.all())
                )
                for cart_item in cart.items.all():
                    product = Product.objects.select_for_update().get(id=cart_item.product.id)
                    if product.stock < cart_item.quantity:
                        raise ValidationError(f"Not enough stock for {product.name}. Order cannot be placed.")
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=cart_item.quantity,
                        price=product.price
                    )
                    product.stock -= cart_item.quantity
                    product.save()
                cart.items.all().delete()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)