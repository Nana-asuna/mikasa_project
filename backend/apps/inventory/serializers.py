from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import Category, Supplier, InventoryItem, StockMovement, PurchaseOrder, PurchaseOrderItem

class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    subcategories = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class SupplierSerializer(serializers.ModelSerializer):
    """Serializer pour les fournisseurs"""
    
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer pour les articles d'inventaire"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'total_value', 'status')
    
    def validate_current_stock(self, value):
        """Validation du stock"""
        if value < 0:
            raise serializers.ValidationError(_("Le stock ne peut pas être négatif."))
        return value
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer pour les mouvements de stock"""
    item_name = serializers.CharField(source='item.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'created_by')
    
    def validate_quantity(self, value):
        """Validation de la quantité"""
        if value <= 0:
            raise serializers.ValidationError(_("La quantité doit être positive."))
        return value
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer pour les articles de commande"""
    item_name = serializers.CharField(source='item.name', read_only=True)
    is_fully_received = serializers.ReadOnlyField()
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        read_only_fields = ('id', 'total_price')

class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes d'achat"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'order_number')
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
