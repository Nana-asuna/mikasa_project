from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
import logging

from .models import Child, ChildNote, ChildDocument, MedicalRecord
from .serializers import (
    ChildSerializer, ChildCreateSerializer, ChildPublicSerializer,
    ChildNoteSerializer, ChildDocumentSerializer, MedicalRecordSerializer,
    ChildStatisticsSerializer
)
from apps.core.permissions import HasRolePermission, IsOwnerOrAdmin
from apps.core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

class ChildListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des enfants"""
    queryset = Child.objects.all()  # type: ignore[attr-defined]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'gender', 'case_worker']
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['first_name', 'last_name', 'date_of_birth', 'arrival_date']
    ordering = ['last_name', 'first_name']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChildCreateSerializer
        return ChildSerializer
    
    def get_queryset(self):
        """Filtre les enfants selon les permissions de l'utilisateur"""
        user = self.request.user
        queryset = Child.objects.all()  # type: ignore[attr-defined]
        
        if user.role == 'visiteur':
            # Les visiteurs ne voient que les enfants à parrainer (données publiques)
            queryset = queryset.filter(status='a_parrainer', is_confidential=False)
        elif user.role == 'parrain':
            # Les parrains voient leurs enfants parrainés + enfants à parrainer
            queryset = queryset.filter(
                Q(sponsor=user) | Q(status='a_parrainer', is_confidential=False)
            )
        elif user.role in ['soignant', 'assistant_social']:
            # Personnel soignant voit tous les enfants non confidentiels + ceux qu'ils suivent
            if user.has_perm('children.view_confidential_child'):
                queryset = queryset.all()
            else:
                queryset = queryset.filter(
                    Q(is_confidential=False) | Q(case_worker=user)
                )
        elif user.role != 'admin':
            # Autres rôles : accès limité
            queryset = queryset.filter(is_confidential=False)
        
        return queryset
    
    def perform_create(self, serializer):
        """Vérifie les permissions avant création"""
        if not self.request.user.role in ['admin', 'assistant_social']:
            raise PermissionDenied(_("Vous n'avez pas les permissions pour créer un dossier d'enfant."))
        
        serializer.save(created_by=self.request.user)
        logger.info(f"Nouvel enfant créé par {self.request.user.email}")

class ChildDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer un enfant"""
    queryset = Child.objects.all()  # type: ignore[attr-defined]
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Vérifie les permissions d'accès à l'enfant"""
        obj = super().get_object()
        
        if not obj.can_be_viewed_by(self.request.user):
            raise PermissionDenied(_("Vous n'avez pas accès à ce dossier."))
        
        return obj
    
    def perform_update(self, serializer):
        """Vérifie les permissions avant modification"""
        if not self.request.user.role in ['admin', 'assistant_social']:
            if not (self.request.user.role == 'soignant' and 
                   self.get_object().case_worker == self.request.user):
                raise PermissionDenied(_("Vous n'avez pas les permissions pour modifier ce dossier."))
        
        serializer.save()
        logger.info(f"Dossier enfant modifié par {self.request.user.email}")
    
    def perform_destroy(self, instance):
        """Vérifie les permissions avant suppression"""
        if not self.request.user.role == 'admin':
            raise PermissionDenied(_("Seuls les administrateurs peuvent supprimer un dossier d'enfant."))
        
        logger.warning(f"Dossier enfant supprimé par {self.request.user.email}: {instance.full_name}")
        instance.delete()

class PublicChildrenView(generics.ListAPIView):
    """Vue publique pour les enfants à parrainer"""
    queryset = Child.objects.filter(status='a_parrainer', is_confidential=False)  # type: ignore[attr-defined]
    serializer_class = ChildPublicSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Retourne uniquement les enfants à parrainer non confidentiels"""
        return Child.objects.filter(  # type: ignore[attr-defined]
            status='a_parrainer',
            is_confidential=False
        ).order_by('arrival_date')  # type: ignore[attr-defined]

class ChildNotesView(generics.ListCreateAPIView):
    """Vue pour les notes sur les enfants"""
    serializer_class = ChildNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        child_id = self.kwargs['child_id']
        try:
            child = Child.objects.get(id=child_id)  # type: ignore[attr-defined]
            if not child.can_be_viewed_by(self.request.user):
                raise PermissionDenied(_("Vous n'avez pas accès à ce dossier."))
        except Child.DoesNotExist:  # type: ignore[attr-defined]
            return ChildNote.objects.none()  # type: ignore[attr-defined]
        
        queryset = ChildNote.objects.filter(child_id=child_id)  # type: ignore[attr-defined]
        
        # Filtrer les notes confidentielles
        if not self.request.user.role in ['admin', 'assistant_social']:
            queryset = queryset.filter(is_confidential=False)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        child_id = self.kwargs['child_id']
        try:
            child = Child.objects.get(id=child_id)  # type: ignore[attr-defined]
            if not child.can_be_viewed_by(self.request.user):
                raise PermissionDenied(_("Vous n'avez pas accès à ce dossier."))
        except Child.DoesNotExist:  # type: ignore[attr-defined]
            raise PermissionDenied(_("Enfant non trouvé."))
        
        serializer.save(child=child, author=self.request.user)

class ChildDocumentsView(generics.ListCreateAPIView):
    """Vue pour les documents des enfants"""
    serializer_class = ChildDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        child_id = self.kwargs['child_id']
        try:
            child = Child.objects.get(id=child_id)  # type: ignore[attr-defined]
            if not child.can_be_viewed_by(self.request.user):
                raise PermissionDenied(_("Vous n'avez pas accès à ce dossier."))
        except Child.DoesNotExist:  # type: ignore[attr-defined]
            return ChildDocument.objects.none()  # type: ignore[attr-defined]
        
        queryset = ChildDocument.objects.filter(child_id=child_id)  # type: ignore[attr-defined]
        
        # Filtrer les documents confidentiels
        if not self.request.user.role in ['admin', 'assistant_social']:
            queryset = queryset.filter(is_confidential=False)
        
        return queryset.order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        child_id = self.kwargs['child_id']
        try:
            child = Child.objects.get(id=child_id)  # type: ignore[attr-defined]
            if not child.can_be_viewed_by(self.request.user):
                raise PermissionDenied(_("Vous n'avez pas accès à ce dossier."))
        except Child.DoesNotExist:  # type: ignore[attr-defined]
            raise PermissionDenied(_("Enfant non trouvé."))
        
        if not self.request.user.role in ['admin', 'assistant_social', 'soignant']:
            raise PermissionDenied(_("Vous n'avez pas les permissions pour ajouter des documents."))
        
        serializer.save(child=child, uploaded_by=self.request.user)

class MedicalRecordsView(generics.ListCreateAPIView):
    """Vue pour les dossiers médicaux"""
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        child_id = self.kwargs['child_id']
        try:
            child = Child.objects.get(id=child_id)  # type: ignore[attr-defined]
            if not child.can_be_viewed_by(self.request.user):
                raise PermissionDenied(_("Vous n'avez pas accès à ce dossier."))
        except Child.DoesNotExist:  # type: ignore[attr-defined]
            return MedicalRecord.objects.none()  # type: ignore[attr-defined]
        
        # Seul le personnel médical peut voir les dossiers médicaux
        if not self.request.user.role in ['admin', 'soignant', 'assistant_social']:
            raise PermissionDenied(_("Vous n'avez pas accès aux dossiers médicaux."))
        
        return MedicalRecord.objects.filter(child_id=child_id).order_by('-visit_date')  # type: ignore[attr-defined]
    
    def perform_create(self, serializer):
        child_id = self.kwargs['child_id']
        try:
            child = Child.objects.get(id=child_id)  # type: ignore[attr-defined]
        except Child.DoesNotExist:  # type: ignore[attr-defined]
            raise PermissionDenied(_("Enfant non trouvé."))
        
        if not self.request.user.role in ['admin', 'soignant']:
            raise PermissionDenied(_("Seul le personnel médical peut créer des dossiers médicaux."))
        
        serializer.save(child=child, created_by=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def children_statistics(request):
    """Statistiques sur les enfants"""
    if not request.user.role in ['admin', 'assistant_social']:
        return Response(
            {'error': _('Accès non autorisé.')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Statistiques de base
    total_children = Child.objects.count()  # type: ignore[attr-defined]
    
    # Par statut
    children_by_status = dict(
        Child.objects.values('status').annotate(count=Count('status')).values_list('status', 'count')  # type: ignore[attr-defined]
    )
    
    # Par genre
    children_by_gender = dict(
        Child.objects.values('gender').annotate(count=Count('gender')).values_list('gender', 'count')  # type: ignore[attr-defined]
    )
    
    # Par groupe d'âge
    from datetime import date, timedelta
    today = date.today()
    
    age_groups = {
        '0-2': Child.objects.filter(date_of_birth__gte=today - timedelta(days=2*365)).count(),  # type: ignore[attr-defined]
        '3-5': Child.objects.filter(                                  
            date_of_birth__gte=today - timedelta(days=5*365),
            date_of_birth__lt=today - timedelta(days=2*365)
        ).count(),  # type: ignore[attr-defined]
        '6-10': Child.objects.filter(             # type: ignore[attr-defined]
            date_of_birth__gte=today - timedelta(days=10*365),
            date_of_birth__lt=today - timedelta(days=5*365)
        ).count(),  # type: ignore[attr-defined]
        '11-15': Child.objects.filter(# type: ignore[attr-defined]
            date_of_birth__gte=today - timedelta(days=15*365),
            date_of_birth__lt=today - timedelta(days=10*365)
        ).count(),  # type: ignore[attr-defined]
        '16+': Child.objects.filter(date_of_birth__lt=today - timedelta(days=15*365)).count(),  # type: ignore[attr-defined]
    }
    
    # Arrivées récentes (30 derniers jours)
    recent_arrivals = Child.objects.filter(# type: ignore[attr-defined]
        arrival_date__gte=today - timedelta(days=30)
    ).count()
    
    
    
    statistics = {
        'total_children': total_children,
        'children_by_status': children_by_status,
        'children_by_gender': children_by_gender,
        'children_by_age_group': age_groups,
        'recent_arrivals': recent_arrivals,
    }
    
    serializer = ChildStatisticsSerializer(statistics)
    return Response(serializer.data)
