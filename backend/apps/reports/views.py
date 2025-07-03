from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import logging

from apps.children.models import Child
from apps.donations.models import Donation
from apps.inventory.models import InventoryItem
from apps.families.models import Family, Placement

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_children_report(request):
    """Génère un rapport PDF des enfants"""
    if not request.user.role in ['admin', 'assistant_social']:
        return Response(
            {'error': _('Accès non autorisé.')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Créer le PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Titre
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Rapport des Enfants - Orphelinat Mikasa")
    
    # Données
    children = Child.objects.all()
    y_position = 700
    
    p.setFont("Helvetica", 12)
    for child in children:
        if y_position < 100:
            p.showPage()
            y_position = 750
        
        p.drawString(100, y_position, f"{child.full_name} - {child.age} ans - {child.get_status_display()}")
        y_position -= 20
    
    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_enfants.pdf"'
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_statistics(request):
    """Statistiques pour le dashboard"""
    user = request.user
    
    if user.role == 'admin':
        stats = {
            'total_children': Child.objects.count(),
            'total_families': Family.objects.count(),
            'total_donations': Donation.objects.count(),
            'pending_approvals': user.__class__.objects.filter(status='pending').count(),
        }
    elif user.role == 'medecin':
        stats = {
            'my_patients': Child.objects.filter(case_worker=user).count(),
            'medical_visits_today': 0,  # À implémenter avec le planning
            'urgent_cases': Child.objects.filter(
                medical_conditions__isnull=False
            ).exclude(medical_conditions='').count(),
        }
    elif user.role == 'assistant_social':
        stats = {
            'assigned_children': Child.objects.filter(case_worker=user).count(),
            'pending_placements': Placement.objects.filter(status='planned').count(),
            'family_visits_this_week': 0,  # À implémenter
        }
    else:
        stats = {
            'message': 'Bienvenue dans votre espace personnel'
        }
    
    return Response(stats)
