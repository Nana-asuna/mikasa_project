from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
import logging

from .models import Category, Supplier, InventoryItem, StockMovement, PurchaseOrder
from .serializers import (
    CategorySerializer, SupplierSerializer, InventoryItemSerializer,
    StockMovementSerializer, PurchaseOrderSerializer
)
from apps.core.permissions import CanManageInventory
from apps.core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

class CategoryListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']

class InventoryItemListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des articles"""
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'supplier']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'current_stock', 'created_at']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Permissions selon la méthode"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageInventory()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        if user.role in ['admin', 'logisticien', 'soignant']:
            return InventoryItem.objects.filter(is_active=True)
        else:
            return InventoryItem.objects.none()

class InventoryItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer un article"""
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Permissions selon la méthode"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), CanManageInventory()]
        return [permissions.IsAuthenticated()]

class StockMovementListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des mouvements de stock"""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'movement_type']
    ordering = ['-movement_date']
    pagination_class = StandardResultsSetPagination

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def inventory_statistics(request):
    """Statistiques de l'inventaire"""
    if not request.user.role in ['admin', 'logisticien']:
        return Response(
            {'error': _('Accès non autorisé.')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Statistiques générales
    total_items = InventoryItem.objects.filter(is_active=True).count()
    total_value = InventoryItem.objects.filter(is_active=True).aggregate(
        total=Sum('total_value')
    )['total'] or 0
    
    # Articles en stock faible
    low_stock_items = InventoryItem.objects.filter(
        current_stock__lte=F('minimum_stock'),
        is_active=True
    ).count()
    
    # Articles expirés
    from datetime import date
    expired_items = InventoryItem.objects.filter(
        expiry_date__lt=date.today(),
        is_active=True
    ).count()
    
    statistics = {
        'total_items': total_items,
        'total_value': float(total_value),
        'low_stock_items': low_stock_items,
        'expired_items': expired_items,
        'out_of_stock_items': InventoryItem.objects.filter(
            current_stock=0, is_active=True
        ).count(),
    }
    
    return Response(statistics)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageInventory])
def bulk_stock_update(request):
    """Mise à jour en lot du stock"""
    updates = request.data.get('updates', [])
    
    if not updates:
        return Response(
            {'error': _('Aucune mise à jour fournie.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    updated_items = []
    errors = []
    
    for update in updates:
        try:
            item = InventoryItem.objects.get(id=update['item_id'])
            
            # Créer un mouvement de stock
            StockMovement.objects.create(
                item=item,
                movement_type='adjustment',
                quantity=update['new_quantity'],
                reason=update.get('reason', 'Ajustement en lot'),
                movement_date=timezone.now(),
                created_by=request.user
            )
            
            updated_items.append(item.name)
            
        except InventoryItem.DoesNotExist:
            errors.append(f"Article {update['item_id']} non trouvé")
        except Exception as e:
            errors.append(f"Erreur pour {update['item_id']}: {str(e)}")
    
    return Response({
        'updated_items': updated_items,
        'errors': errors,
        'success_count': len(updated_items)
    })
