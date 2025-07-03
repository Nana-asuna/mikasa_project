from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
import logging

from .models import Report
from apps.accounts.models import User

logger = logging.getLogger(__name__)

@shared_task
def send_daily_reports():
    """Envoie les rapports quotidiens programmés"""
    
    # Rapports programmés pour aujourd'hui
    today = timezone.now().date()
    scheduled_reports = Report.objects.filter(
        is_scheduled=True,
        schedule_frequency='daily',
        next_generation_date__date=today
    )
    
    generated_count = 0
    
    for report in scheduled_reports:
        try:
            # Ici, vous pourriez déclencher la génération du rapport
            # generate_report_task.delay(report.id)
            
            # Mettre à jour la prochaine date de génération
            report.next_generation_date = timezone.now() + timedelta(days=1)
            report.save()
            
            generated_count += 1
            logger.info(f"Rapport quotidien programmé: {report.title}")
            
        except Exception as e:
            logger.error(f"Erreur génération rapport {report.id}: {str(e)}")
    
    logger.info(f"Rapports quotidiens traités: {generated_count}")
    return f"Rapports traités: {generated_count}"

@shared_task
def generate_report_task(report_id):
    """Génère un rapport de manière asynchrone"""
    try:
        report = Report.objects.get(id=report_id)
        report.status = 'generating'
        report.save()
        
        # Ici, vous implémenteriez la logique de génération selon le type de rapport
        # Par exemple, pour un rapport d'enfants:
        if report.report_type == 'children_summary':
            # Générer le rapport des enfants
            pass
        elif report.report_type == 'donations_summary':
            # Générer le rapport des dons
            pass
        
        # Marquer comme terminé
        report.status = 'completed'
        report.generated_at = timezone.now()
        report.save()
        
        logger.info(f"Rapport généré avec succès: {report.title}")
        return f"Rapport généré: {report.title}"
        
    except Report.DoesNotExist:
        logger.error(f"Rapport {report_id} non trouvé")
        return f"Erreur: Rapport {report_id} non trouvé"
    except Exception as e:
        logger.error(f"Erreur génération rapport {report_id}: {str(e)}")
        # Marquer comme échoué
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
        except:
            pass
        return f"Erreur génération rapport: {str(e)}"
