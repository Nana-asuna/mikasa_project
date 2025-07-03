from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

class NotificationTemplate(models.Model):
    """Modèles de notifications"""
    
    NOTIFICATION_TYPES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Notification push')),
        ('in_app', _('Notification in-app')),
    ]
    
    TRIGGER_EVENTS = [
        ('child_arrival', _('Arrivée d\'enfant')),
        ('medical_appointment', _('Rendez-vous médical')),
        ('donation_received', _('Don reçu')),
        ('stock_low', _('Stock faible')),
        ('task_due', _('Tâche échue')),
        ('family_visit', _('Visite de famille')),
        ('document_expiry', _('Expiration de document')),
        ('birthday', _('Anniversaire')),
        ('custom', _('Personnalisé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    notification_type = models.CharField(_('Type de notification'), max_length=20, choices=NOTIFICATION_TYPES)
    trigger_event = models.CharField(_('Événement déclencheur'), max_length=30, choices=TRIGGER_EVENTS)
    
    # Contenu du modèle
    subject_template = models.CharField(_('Modèle de sujet'), max_length=200, blank=True)
    body_template = models.TextField(_('Modèle de corps'))
    html_template = models.TextField(_('Modèle HTML'), blank=True)
    
    # Configuration
    is_active = models.BooleanField(_('Actif'), default=True)  # type: ignore[attr-defined]
    send_immediately = models.BooleanField(_('Envoyer immédiatement'), default=True)  # type: ignore[attr-defined]
    delay_minutes = models.PositiveIntegerField(_('Délai (minutes)'), default=0)  # type: ignore[attr-defined]
    
    # Destinataires
    default_recipients = models.JSONField(_('Destinataires par défaut'), default=list)
    recipient_roles = models.JSONField(_('Rôles destinataires'), default=list)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_notification_templates'
    )
    
    class Meta:
        verbose_name = _('Modèle de notification')
        verbose_name_plural = _('Modèles de notifications')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"  # type: ignore[attr-defined]

class Notification(models.Model):
    """Notifications envoyées"""
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('sent', _('Envoyée')),
        ('delivered', _('Livrée')),
        ('read', _('Lue')),
        ('failed', _('Échouée')),
    ]
    
    PRIORITY_LEVELS = [
        ('low', _('Faible')),
        ('medium', _('Moyenne')),
        ('high', _('Élevée')),
        ('urgent', _('Urgente')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    
    # Contenu
    notification_type = models.CharField(_('Type'), max_length=20, choices=NotificationTemplate.NOTIFICATION_TYPES)
    subject = models.CharField(_('Sujet'), max_length=200, blank=True)
    message = models.TextField(_('Message'))
    html_content = models.TextField(_('Contenu HTML'), blank=True)
    
    # Métadonnées
    priority = models.CharField(_('Priorité'), max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dates
    scheduled_at = models.DateTimeField(_('Planifiée pour'), null=True, blank=True)
    sent_at = models.DateTimeField(_('Envoyée le'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Livrée le'), null=True, blank=True)
    read_at = models.DateTimeField(_('Lue le'), null=True, blank=True)
    
    # Informations d'envoi
    recipient_email = models.EmailField(_('Email destinataire'), blank=True)
    recipient_phone = models.CharField(_('Téléphone destinataire'), max_length=20, blank=True)
    external_id = models.CharField(_('ID externe'), max_length=200, blank=True)
    error_message = models.TextField(_('Message d\'erreur'), blank=True)
    
    # Données contextuelles
    context_data = models.JSONField(_('Données contextuelles'), default=dict, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} -> {self.recipient.get_full_name()}"  # type: ignore[attr-defined]
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = timezone.now()  # type: ignore[attr-defined]
            self.save(update_fields=['status', 'read_at'])

class NotificationPreference(models.Model):
    """Préférences de notification des utilisateurs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Préférences par type
    email_enabled = models.BooleanField(_('Notifications email'), default=True)  # type: ignore[attr-defined]
    sms_enabled = models.BooleanField(_('Notifications SMS'), default=False)  # type: ignore[attr-defined]
    push_enabled = models.BooleanField(_('Notifications push'), default=True)  # type: ignore[attr-defined]
    in_app_enabled = models.BooleanField(_('Notifications in-app'), default=True)  # type: ignore[attr-defined]
    
    # Préférences par événement
    child_events = models.BooleanField(_('Événements enfants'), default=True)  # type: ignore[attr-defined]
    medical_events = models.BooleanField(_('Événements médicaux'), default=True)  # type: ignore[attr-defined]
    donation_events = models.BooleanField(_('Événements dons'), default=True)  # type: ignore[attr-defined]
    inventory_events = models.BooleanField(_('Événements inventaire'), default=True)  # type: ignore[attr-defined]
    task_events = models.BooleanField(_('Événements tâches'), default=True)  # type: ignore[attr-defined]
    family_events = models.BooleanField(_('Événements familles'), default=True)  # type: ignore[attr-defined]
    
    # Horaires de notification
    quiet_hours_start = models.TimeField(_('Début heures silencieuses'), default='22:00')
    quiet_hours_end = models.TimeField(_('Fin heures silencieuses'), default='08:00')
    weekend_notifications = models.BooleanField(_('Notifications week-end'), default=False)  # type: ignore[attr-defined]
    
    # Fréquence des résumés
    daily_summary = models.BooleanField(_('Résumé quotidien'), default=False)  # type: ignore[attr-defined] 
    weekly_summary = models.BooleanField(_('Résumé hebdomadaire'), default=True)  # type: ignore[attr-defined]
    monthly_summary = models.BooleanField(_('Résumé mensuel'), default=False)  # type: ignore[attr-defined]
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Préférence de notification')
        verbose_name_plural = _('Préférences de notifications')
    
    def __str__(self):
        return f"Préférences de {self.user.get_full_name()}"  # type: ignore[attr-defined]

class NotificationLog(models.Model):
    """Journal des notifications"""
    
    ACTION_TYPES = [
        ('created', _('Créée')),
        ('sent', _('Envoyée')),
        ('delivered', _('Livrée')),
        ('read', _('Lue')),
        ('failed', _('Échouée')),
        ('cancelled', _('Annulée')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    
    # Action
    action = models.CharField(_('Action'), max_length=20, choices=ACTION_TYPES)
    details = models.TextField(_('Détails'), blank=True)
    
    # Métadonnées techniques
    ip_address = models.GenericIPAddressField(_('Adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    
    # Horodatage
    timestamp = models.DateTimeField(_('Horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Journal de notification')
        verbose_name_plural = _('Journaux de notifications')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.notification.subject} - {self.get_action_display()}"  # type: ignore[attr-defined]
