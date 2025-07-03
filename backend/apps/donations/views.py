from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
import logging

from .models import Donor, Donation, DonationCampaign, RecurringDonation
from .serializers import (
    DonorSerializer, DonationSerializer, DonationCampaignSerializer,
    RecurringDonationSerializer
)
from apps.core.permissions import HasRolePermission, IsOwnerOrAdmin
from apps.core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

class DonorListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des donateurs"""
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['donor_type', 'is_active']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'created_at', 'total_donations']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        if user.role in ['admin', 'assistant_social']:
            return Donor.objects.all()
        elif user.role in ['donateur', 'parrain']:
            return Donor.objects.filter(user=user)
        else:
            return Donor.objects.filter(is_active=True)

class DonorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer un donateur"""
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

class DonationListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des dons"""
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['donation_type', 'status', 'donor']
    search_fields = ['description', 'donor__name']
    ordering_fields = ['donation_date', 'amount']
    ordering = ['-donation_date']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        if user.role in ['admin', 'assistant_social']:
            return Donation.objects.all()
        elif user.role in ['donateur', 'parrain']:
            return Donation.objects.filter(donor__user=user)
        else:
            return Donation.objects.filter(status='confirmed')

class DonationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer un don"""
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

class DonationCampaignListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des campagnes"""
    queryset = DonationCampaign.objects.all()
    serializer_class = DonationCampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'campaign_type']
    ordering_fields = ['start_date', 'target_amount']
    ordering = ['-start_date']
    
    def perform_create(self, serializer):
        """Création avec l'utilisateur créateur"""
        serializer.save(created_by=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def donation_statistics(request):
    """Statistiques des dons"""
    if not request.user.role in ['admin', 'assistant_social']:
        return Response(
            {'error': _('Accès non autorisé.')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Statistiques générales
    total_donations = Donation.objects.aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id')
    )
    
    # Dons par type
    donations_by_type = dict(
        Donation.objects.values('donation_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).values_list('donation_type', 'total')
    )
    
    # Dons récents (30 derniers jours)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_donations = Donation.objects.filter(
        donation_date__gte=thirty_days_ago
    ).aggregate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    statistics = {
        'total_amount': total_donations['total_amount'] or 0,
        'total_count': total_donations['total_count'] or 0,
        'donations_by_type': donations_by_type,
        'recent_donations': recent_donations,
        'active_donors': Donor.objects.filter(is_active=True).count(),
        'active_campaigns': DonationCampaign.objects.filter(status='active').count(),
    }
    
    return Response(statistics)
