from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import Event
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)

@shared_task
def send_appointment_reminders():
    """Envoie des rappels pour les événements à venir"""
    
    # Événements dans les prochaines 24 heures
    tomorrow = timezone.now() + timedelta(hours=24)
    upcoming_events = Event.objects.filter(
        start_datetime__gte=timezone.now(),
        start_datetime__lte=tomorrow,
        reminder_sent=False,
        reminder_minutes__isnull=False
    )
    
    sent_count = 0
    
    for event in upcoming_events:
        # Calculer le moment d'envoi du rappel
        reminder_time = event.start_datetime - timedelta(minutes=event.reminder_minutes)
        
        if timezone.now() >= reminder_time:
            # Envoyer des notifications aux participants
            participants = list(event.staff_members.all())
            if event.organizer:
                participants.append(event.organizer)
            
            for participant in participants:
                try:
                    Notification.objects.create(
                        recipient=participant,
                        notification_type='in_app',
                        subject=f"Rappel: {event.title}",
                        message=f"Votre événement '{event.title}' commence dans {event.reminder_minutes} minutes.",
                        priority='high',
                        context_data={
                            'event_id': str(event.id),
                            'event_type': event.event_type,
                            'start_time': event.start_datetime.isoformat(),
                        }
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Erreur envoi rappel à {participant.email}: {str(e)}")
            
            # Marquer le rappel comme envoyé
            event.reminder_sent = True
            event.save()
    
    logger.info(f"Rappels d'événements envoyés: {sent_count} notifications")
    return f"Rappels envoyés: {sent_count} notifications"
