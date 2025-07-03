from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

from .models import InventoryItem
from apps.accounts.models import User

logger = logging.getLogger(__name__)

@shared_task
def check_low_stock():
    """Vérifie les articles en stock faible et envoie des alertes"""
    
    # Articles en stock faible
    low_stock_items = InventoryItem.objects.filter(
        current_stock__lte=models.F('minimum_stock'),
        is_active=True
    )
    
    if not low_stock_items.exists():
        return "Aucun article en stock faible"
    
    # Récupérer les utilisateurs à notifier
    users_to_notify = User.objects.filter(
        role__in=['admin', 'logisticien'],
        is_active=True
    )
    
    # Préparer l'email
    context = {
        'low_stock_items': low_stock_items,
        'count': low_stock_items.count()
    }
    
    subject = f"Alerte Stock Faible - {low_stock_items.count()} articles"
    message = render_to_string('emails/low_stock_alert.html', context)
    
    # Envoyer les emails
    sent_count = 0
    for user in users_to_notify:
        try:
            send_mail(
                subject=subject,
                message='',
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Erreur envoi email stock faible à {user.email}: {str(e)}")
    
    logger.info(f"Alertes stock faible envoyées: {sent_count} emails")
    return f"Alertes envoyées à {sent_count} utilisateurs pour {low_stock_items.count()} articles"
