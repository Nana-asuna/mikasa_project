from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import RecurringDonation, Donation

logger = logging.getLogger(__name__)

@shared_task
def process_recurring_donations():
    """Traite les dons récurrents dus"""
    today = timezone.now().date()
    
    # Récupérer les dons récurrents dus
    due_donations = RecurringDonation.objects.filter(
        status='active',
        next_payment_date__lte=today
    )
    
    processed_count = 0
    
    for recurring_donation in due_donations:
        try:
            # Créer un nouveau don
            Donation.objects.create(
                donor=recurring_donation.donor,
                donation_type='money',
                amount=recurring_donation.amount,
                donation_date=timezone.now(),
                status='confirmed',
                payment_method=recurring_donation.payment_method,
                description=f"Don récurrent - {recurring_donation.get_frequency_display()}"
            )
            
            # Mettre à jour la prochaine date de paiement
            recurring_donation.next_payment_date = recurring_donation.calculate_next_payment_date()
            recurring_donation.save()
            
            processed_count += 1
            logger.info(f"Don récurrent traité: {recurring_donation.donor.name} - {recurring_donation.amount}€")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du don récurrent {recurring_donation.id}: {str(e)}")
    
    logger.info(f"Traitement des dons récurrents terminé: {processed_count} dons traités")
    return processed_count
