from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Event, Schedule, Availability, Task, Shift
from .serializers import (
    EventSerializer, ScheduleSerializer, AvailabilitySerializer,
    TaskSerializer, ShiftSerializer
)
from apps.core.permissions import HasRolePermission
from apps.core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

class EventListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des événements"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['start_datetime', 'priority']
    ordering = ['start_datetime']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        if user.role in ['admin', 'assistant_social']:
            return Event.objects.all()
        elif user.role in ['soignant']:
            return Event.objects.filter(
                Q(organizer=user) | Q(staff_members=user)
            ).distinct()
        else:
            return Event.objects.filter(organizer=user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer un événement"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Vérifie les permissions d'accès"""
        obj = super().get_object()
        user = self.request.user
        
        if not obj.can_be_modified_by(user) and self.request.method in ['PUT', 'PATCH', 'DELETE']:
            raise PermissionDenied(_("Vous n'avez pas les permissions pour modifier cet événement."))
        
        return obj

class TaskListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des tâches"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['-priority', 'due_date']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        if user.role in ['admin', 'assistant_social']:
            return Task.objects.all()
        else:
            return Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).distinct()

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer une tâche"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

class ShiftListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des équipes"""
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['shift_type', 'date']
    ordering = ['date', 'start_time']
    
    def get_permissions(self):
        """Permissions selon la méthode"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), HasRolePermission(['admin', 'assistant_social'])]
        return [permissions.IsAuthenticated()]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def planning_statistics(request):
    """Statistiques du planning"""
    user = request.user
    
    # Événements à venir
    upcoming_events = Event.objects.filter(
        start_datetime__gte=timezone.now(),
        start_datetime__lte=timezone.now() + timedelta(days=7)
    )
    
    if user.role not in ['admin', 'assistant_social']:
        upcoming_events = upcoming_events.filter(
            Q(organizer=user) | Q(staff_members=user)
        ).distinct()
    
    # Tâches en cours
    pending_tasks = Task.objects.filter(status='pending')
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    )
    
    if user.role not in ['admin', 'assistant_social']:
        pending_tasks = pending_tasks.filter(assigned_to=user)
        overdue_tasks = overdue_tasks.filter(assigned_to=user)
    
    statistics = {
        'upcoming_events': upcoming_events.count(),
        'events_today': upcoming_events.filter(
            start_datetime__date=timezone.now().date()
        ).count(),
        'pending_tasks': pending_tasks.count(),
        'overdue_tasks': overdue_tasks.count(),
        'completed_tasks_this_week': Task.objects.filter(
            status='completed',
            completed_date__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    return Response(statistics)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def calendar_events(request):
    """Événements pour le calendrier"""
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if not start_date or not end_date:
        return Response(
            {'error': _('Dates de début et fin requises.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
    except ValueError:
        return Response(
            {'error': _('Format de date invalide.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    events = Event.objects.filter(
        start_datetime__gte=start_datetime,
        end_datetime__lte=end_datetime
    )
    
    user = request.user
    if user.role not in ['admin', 'assistant_social']:
        events = events.filter(
            Q(organizer=user) | Q(staff_members=user)
        ).distinct()
    
    # Format pour le calendrier
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': str(event.id),
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'allDay': event.all_day,
            'color': {
                'medical_visit': '#dc3545',
                'activity': '#28a745',
                'education': '#007bff',
                'recreation': '#ffc107',
                'meeting': '#6c757d',
            }.get(event.event_type, '#17a2b8'),
            'extendedProps': {
                'type': event.event_type,
                'status': event.status,
                'priority': event.priority,
                'location': event.location,
            }
        })
    
    return Response(calendar_events)
