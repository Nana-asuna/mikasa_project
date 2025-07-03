from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_notification(request):
    """Envoie une notification"""
    if not request.user.role in ['admin', 'assistant_social']:
        return Response(
            {'error': _('Accès non autorisé.')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    recipient_email = request.data.get('email')
    subject = request.data.get('subject')
    message = request.data.get('message')
    
    if not all([recipient_email, subject, message]):
        return Response(
            {'error': _('Email, sujet et message requis.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Notification envoyée à {recipient_email} par {request.user.email}")
        
        return Response({
            'message': _('Notification envoyée avec succès.')
        })
        
    except Exception as e:
        logger.error(f"Erreur envoi notification: {str(e)}")
        return Response(
            {'error': _('Erreur lors de l\'envoi de la notification.')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
