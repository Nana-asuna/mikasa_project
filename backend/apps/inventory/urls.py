from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    
    # Items
    path('items/', views.InventoryItemListCreateView.as_view(), name='item-list-create'),
    path('items/<uuid:pk>/', views.InventoryItemDetailView.as_view(), name='item-detail'),
    path('items/statistics/', views.inventory_statistics, name='inventory-statistics'),
    path('items/bulk-update/', views.bulk_stock_update, name='bulk-stock-update'),
    
    # Stock movements
    path('movements/', views.StockMovementListCreateView.as_view(), name='movement-list-create'),
    
    # Router URLs
    path('', include(router.urls)),
]
