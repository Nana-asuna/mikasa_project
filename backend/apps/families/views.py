from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
import logging

from .models import Family, FamilyMember, Placement, FamilyVisit
from .serializers import (
    FamilySerializer, FamilyMemberSerializer, PlacementSerializer,
    FamilyVisitSerializer
)
from apps.core.permissions import HasRolePermission
from apps.core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

class FamilyListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des familles"""
    queryset = Family.objects.all()
    serializer_class = FamilySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['family_type', 'status']
    search_fields = ['family_name', 'primary_contact_first_name', 'primary_contact_last_name']
    ordering_fields = ['family_name', 'created_at']
    ordering = ['family_name']
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Permissions selon la méthode"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), HasRolePermission(['admin', 'assistant_social'])]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        if user.role in ['admin', 'assistant_social']:
            return Family.objects.all()
        else:
            return Family.objects.filter(status='approved')

class FamilyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer une famille"""
    queryset = Family.objects.all()
    serializer_class = FamilySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Permissions selon la méthode"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), HasRolePermission(['admin', 'assistant_social'])]
        return [permissions.IsAuthenticated()]

class PlacementListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des placements"""
    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission(['admin', 'assistant_social'])]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['placement_type', 'status', 'family', 'child']
    ordering = ['-start_date']
    pagination_class = StandardResultsSetPagination

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def family_statistics(request):
    """Statistiques des familles"""
    if not request.user.role in ['admin', 'assistant_social']:
        return Response(
            {'error': _('Accès non autorisé.')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    statistics = {
        'total_families': Family.objects.count(),
        'approved_families': Family.objects.filter(status='approved').count(),
        'pending_families': Family.objects.filter(status='pending').count(),
        'active_placements': Placement.objects.filter(status='active').count(),
        'available_families': Family.objects.filter(
            status='approved',
            max_children_capacity__gt=Count('placements')
        ).count(),
    }
    
    return Response(statistics)
