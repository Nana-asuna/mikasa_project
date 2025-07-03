from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Families
    path('', views.FamilyListCreateView.as_view(), name='family-list-create'),
    path('<uuid:pk>/', views.FamilyDetailView.as_view(), name='family-detail'),
    # path('<uuid:pk>/approve/', views.approve_family, name='approve-family'),  # type: ignore[attr-defined]
    path('statistics/', views.family_statistics, name='family-statistics'),
    
    # Placements
    path('placements/', views.PlacementListCreateView.as_view(), name='placement-list-create'),
    # path('placements/<uuid:pk>/', views.PlacementDetailView.as_view(), name='placement-detail'),  # type: ignore[attr-defined]
    
    # Visits
    # path('visits/', views.FamilyVisitListCreateView.as_view(), name='visit-list-create'),  # type: ignore[attr-defined]
    
    # Router URLs
    path('', include(router.urls)),
]
