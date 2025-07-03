from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

class Report(models.Model):
    """Rapports générés"""
    
    REPORT_TYPES = [
        ('children_summary', _('Résumé des enfants')),
        ('donations_summary', _('Résumé des dons')),
        ('inventory_report', _('Rapport d\'inventaire')),  # type: ignore[attr-defined]
        ('financial_report', _('Rapport financier')),
        ('staff_report', _('Rapport du personnel')),
        ('family_report', _('Rapport des familles')),
        ('medical_report', _('Rapport médical')),
        ('custom_report', _('Rapport personnalisé')),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('generating', _('En cours de génération')),
        ('completed', _('Terminé')),
        ('failed', _('Échoué')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    report_type = models.CharField(_('Type de rapport'), max_length=30, choices=REPORT_TYPES)
    
    # Paramètres
    parameters = models.JSONField(_('Paramètres'), default=dict, blank=True)
    date_from = models.DateField(_('Date de début'), null=True, blank=True)
    date_to = models.DateField(_('Date de fin'), null=True, blank=True)
    
    # Format et fichier
    format = models.CharField(_('Format'), max_length=10, choices=FORMAT_CHOICES, default='pdf')
    file = models.FileField(_('Fichier'), upload_to='reports/', null=True, blank=True)
    file_size = models.PositiveIntegerField(_('Taille du fichier'), null=True, blank=True)
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(_('Message d\'erreur'), blank=True)  # type: ignore[attr-defined]
    
    # Planification
    is_scheduled = models.BooleanField(_('Planifié'), default=False)  # type: ignore[attr-defined]
    schedule_frequency = models.CharField(
        _('Fréquence'),
        max_length=20,
        choices=[
            ('daily', _('Quotidien')),
            ('weekly', _('Hebdomadaire')),
            ('monthly', _('Mensuel')),
            ('quarterly', _('Trimestriel')),
            ('yearly', _('Annuel')),
        ],
        blank=True
    )
    next_generation_date = models.DateTimeField(_('Prochaine génération'), null=True, blank=True)
    
    # Accès 
    is_public = models.BooleanField(_('Public'), default=False)  # type: ignore[attr-defined]
    allowed_roles = models.JSONField(_('Rôles autorisés'), default=list, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    generated_at = models.DateTimeField(_('Généré le'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    
    class Meta:
        verbose_name = _('Rapport')
        verbose_name_plural = _('Rapports')
        ordering = ['-created_at']
        permissions = [
            ('can_generate_reports', 'Peut générer des rapports'),
            ('can_view_all_reports', 'Peut voir tous les rapports'),
            ('can_schedule_reports', 'Peut planifier des rapports'),
        ]
    
    def __str__(self):
        return self.title
    
    def can_be_accessed_by(self, user):
        """Vérifie si un utilisateur peut accéder à ce rapport"""
        if user.role == 'admin':
            return True
        if user == self.created_by:
            return True
        if self.is_public:
            return True
        if user.role in self.allowed_roles:
            return True
        return False

class ReportTemplate(models.Model):
    """Modèles de rapports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    report_type = models.CharField(_('Type de rapport'), max_length=30, choices=Report.REPORT_TYPES)
    
    # Configuration
    template_config = models.JSONField(_('Configuration du modèle'), default=dict)
    default_parameters = models.JSONField(_('Paramètres par défaut'), default=dict)
    
    # Requête SQL personnalisée (pour les rapports avancés)
    custom_query = models.TextField(_('Requête personnalisée'), blank=True)
    
    # Mise en forme
    header_template = models.TextField(_('Modèle d\'en-tête'), blank=True)  # type: ignore[attr-defined]    
    footer_template = models.TextField(_('Modèle de pied de page'), blank=True)  # type: ignore[attr-defined]
    css_styles = models.TextField(_('Styles CSS'), blank=True)
    
    # Accès
    is_active = models.BooleanField(_('Actif'), default=True)  # type: ignore[attr-defined]
    allowed_roles = models.JSONField(_('Rôles autorisés'), default=list)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_templates'
    )
    
    class Meta:
        verbose_name = _('Modèle de rapport')
        verbose_name_plural = _('Modèles de rapports')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Dashboard(models.Model):
    """Tableaux de bord personnalisés"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    
    # Configuration
    layout_config = models.JSONField(_('Configuration de mise en page'), default=dict)
    widgets = models.JSONField(_('Widgets'), default=list)
    refresh_interval = models.PositiveIntegerField(_('Intervalle de rafraîchissement (secondes)'), default=300)  # type: ignore[attr-defined]
    
    # Accès
    is_default = models.BooleanField(_('Par défaut'), default=False)  # type: ignore[attr-defined]
    is_public = models.BooleanField(_('Public'), default=False)  # type: ignore[attr-defined]
    allowed_roles = models.JSONField(_('Rôles autorisés'), default=list)
    
    # Propriétaire
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboards'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Tableau de bord')
        verbose_name_plural = _('Tableaux de bord')
        ordering = ['name']
    
    def __str__(self):
        return self.name
