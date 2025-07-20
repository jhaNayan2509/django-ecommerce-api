from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    # We need a write-only field to accept the product ID when adding an item.
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    # A custom field to calculate the grand total of the cart.
    grand_total = serializers.SerializerMethodField()

    message = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'grand_total', 'created_at', 'message']
        read_only_fields = ['user', 'created_at']

    def get_grand_total(self, obj):
        # obj here is the Cart instance. We sum the total_price of all its items.
        return sum(item.total_price for item in obj.items.all())
    
    def get_message(self, obj):
        if obj.items.count() == 0:
            return "Your shopping cart is currently empty."
        return f"You have {obj.items.count()} item(s) in your cart."


# === ORDER SERIALIZERS ===

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'created_at']