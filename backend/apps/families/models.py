from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

class Family(models.Model):
    """Familles d'accueil et adoptives"""
    
    FAMILY_TYPES = [
        ('foster', _('Famille d\'accueil')),
        ('adoptive', _('Famille adoptive')),
        ('both', _('Les deux')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvée')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspendue')),
        ('rejected', _('Rejetée')),
    ]
    
    MARITAL_STATUS = [
        ('single', _('Célibataire')),
        ('married', _('Marié(e)')),
        ('divorced', _('Divorcé(e)')),
        ('widowed', _('Veuf/Veuve')),
        ('partnership', _('Union libre')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    family_name = models.CharField(_('Nom de famille'), max_length=200)
    family_type = models.CharField(_('Type de famille'), max_length=20, choices=FAMILY_TYPES)
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Contact principal
    primary_contact_first_name = models.CharField(_('Prénom contact principal'), max_length=100)
    primary_contact_last_name = models.CharField(_('Nom contact principal'), max_length=100)
    primary_contact_email = models.EmailField(_('Email contact principal'))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés.")
    )
    primary_contact_phone = models.CharField(_('Téléphone principal'), validators=[phone_regex], max_length=17)
    
    # Contact secondaire (optionnel)
    secondary_contact_first_name = models.CharField(_('Prénom contact secondaire'), max_length=100, blank=True)
    secondary_contact_last_name = models.CharField(_('Nom contact secondaire'), max_length=100, blank=True)
    secondary_contact_email = models.EmailField(_('Email contact secondaire'), blank=True)
    secondary_contact_phone = models.CharField(_('Téléphone secondaire'), validators=[phone_regex], max_length=17, blank=True)
    
    # Adresse
    address_line1 = models.CharField(_('Adresse ligne 1'), max_length=200)
    address_line2 = models.CharField(_('Adresse ligne 2'), max_length=200, blank=True)
    city = models.CharField(_('Ville'), max_length=100)
    postal_code = models.CharField(_('Code postal'), max_length=20)
    country = models.CharField(_('Pays'), max_length=100, default='France')
    
    # Informations familiales
    marital_status = models.CharField(_('Statut matrimonial'), max_length=20, choices=MARITAL_STATUS)
    number_of_children = models.PositiveIntegerField(_('Nombre d\'enfants'), default=0)  # type: ignore[attr-defined]
    household_size = models.PositiveIntegerField(_('Taille du foyer'), default=2)  # type: ignore[attr-defined]
    
    # Informations financières
    annual_income = models.DecimalField(
        _('Revenus annuels'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    employment_status_primary = models.CharField(_('Statut emploi principal'), max_length=200, blank=True)
    employment_status_secondary = models.CharField(_('Statut emploi secondaire'), max_length=200, blank=True)
    
    # Préférences d'accueil
    preferred_age_min = models.PositiveIntegerField(_('Âge minimum préféré'), null=True, blank=True)
    preferred_age_max = models.PositiveIntegerField(_('Âge maximum préféré'), null=True, blank=True)
    preferred_gender = models.CharField(
        _('Genre préféré'),
        max_length=10,
        choices=[('M', _('Garçon')), ('F', _('Fille')), ('both', _('Les deux'))],
        default='both'
    )
    max_children_capacity = models.PositiveIntegerField(_('Capacité maximale d\'enfants'), default=1)  # type: ignore[attr-defined]
    special_needs_acceptance = models.BooleanField(_('Accepte les besoins spéciaux'), default=False)  # type: ignore[attr-defined]
    
    # Langues parlées
    languages_spoken = models.CharField(_('Langues parlées'), max_length=200, default='Français')
    
    # Expérience
    previous_foster_experience = models.BooleanField(_('Expérience d\'accueil précédente'), default=False)  # type: ignore[attr-defined]
    previous_adoption_experience = models.BooleanField(_('Expérience d\'adoption précédente'), default=False)  # type: ignore[attr-defined]
    experience_description = models.TextField(_('Description de l\'expérience'), blank=True)
    
    # Motivation
    motivation = models.TextField(_('Motivation'), blank=True)
    expectations = models.TextField(_('Attentes'), blank=True)
    
    # Vérifications
    background_check_completed = models.BooleanField(_('Vérification antécédents terminée'), default=False)  # type: ignore[attr-defined]
    background_check_date = models.DateField(_('Date vérification antécédents'), null=True, blank=True)
    home_study_completed = models.BooleanField(_('Étude du domicile terminée'), default=False)  # type: ignore[attr-defined]
    home_study_date = models.DateField(_('Date étude du domicile'), null=True, blank=True)
    references_checked = models.BooleanField(_('Références vérifiées'), default=False)  # type: ignore[attr-defined]
    
    # Dates importantes
    application_date = models.DateField(_('Date de candidature'))
    approval_date = models.DateField(_('Date d\'approbation'), null=True, blank=True)
    last_review_date = models.DateField(_('Dernière révision'), null=True, blank=True)
    next_review_date = models.DateField(_('Prochaine révision'), null=True, blank=True)
    
    # Assignation
    case_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assigned_families',
        limit_choices_to={'role__in': ['assistant_social', 'admin']},
        verbose_name=_('Assistant social responsable')
    )
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    internal_notes = models.TextField(_('Notes internes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='created_families',
        verbose_name=_('Créé par')
    )
    
    class Meta:
        verbose_name = _('Famille')
        verbose_name_plural = _('Familles')
        ordering = ['family_name']
        permissions = [
            ('can_approve_families', 'Peut approuver les familles'),
            ('can_view_financial_info', 'Peut voir les informations financières'),
        ]
    
    def __str__(self):
        return f"{self.family_name} - {self.get_family_type_display()}"  # type: ignore[attr-defined]
    
    @property
    def primary_contact_full_name(self):
        """Nom complet du contact principal"""
        return f"{self.primary_contact_first_name} {self.primary_contact_last_name}"
    
    @property
    def secondary_contact_full_name(self):
        """Nom complet du contact secondaire"""
        if self.secondary_contact_first_name and self.secondary_contact_last_name:
            return f"{self.secondary_contact_first_name} {self.secondary_contact_last_name}"
        return ""
    
    @property
    def current_children_count(self):
        """Nombre d'enfants actuellement placés"""
        return self.placements.filter(status='active').count()  # type: ignore[attr-defined]
    
    @property
    def available_capacity(self):
        """Capacité disponible"""
        return max(0, self.max_children_capacity - self.current_children_count)
    
    @property
    def is_available(self):
        """Vérifie si la famille est disponible pour un nouveau placement"""
        return (self.status == 'active' and 
                self.available_capacity > 0)

class FamilyMember(models.Model):
    """Membres de la famille"""
    
    RELATIONSHIP_CHOICES = [
        ('parent', _('Parent')),
        ('child', _('Enfant')),
        ('grandparent', _('Grand-parent')),
        ('sibling', _('Frère/Sœur')),
        ('other_relative', _('Autre parent')),
        ('non_relative', _('Non-parent')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members')
    
    # Informations personnelles
    first_name = models.CharField(_('Prénom'), max_length=100)
    last_name = models.CharField(_('Nom'), max_length=100)
    date_of_birth = models.DateField(_('Date de naissance'))
    relationship = models.CharField(_('Relation'), max_length=20, choices=RELATIONSHIP_CHOICES)
    
    # Informations supplémentaires
    occupation = models.CharField(_('Profession'), max_length=200, blank=True)
    education_level = models.CharField(_('Niveau d\'éducation'), max_length=200, blank=True)
    health_conditions = models.TextField(_('Conditions de santé'), blank=True)
    
    # Vérifications
    background_check_completed = models.BooleanField(_('Vérification antécédents'), default=False)  # type: ignore[attr-defined]
    background_check_date = models.DateField(_('Date vérification'), null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Membre de famille')
        verbose_name_plural = _('Membres de famille')
        ordering = ['relationship', 'date_of_birth']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_relationship_display()})"  # type: ignore[attr-defined]
    
    @property
    def age(self):
        """Calcule l'âge"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (  # type: ignore[attr-defined]
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)  # type: ignore[attr-defined]
        )

class Placement(models.Model):
    """Placements d'enfants dans les familles"""
    
    PLACEMENT_TYPES = [
        ('foster_care', _('Placement familial')),
        ('adoption', _('Adoption')),
        ('respite_care', _('Accueil temporaire')),
        ('emergency_care', _('Accueil d\'urgence')),
    ]
    
    STATUS_CHOICES = [
        ('planned', _('Planifié')),
        ('active', _('Actif')),
        ('completed', _('Terminé')),
        ('disrupted', _('Interrompu')),
        ('cancelled', _('Annulé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    child = models.ForeignKey(
        'children.Child',
        on_delete=models.CASCADE,
        related_name='placements'
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='placements'
    )
    
    # Type et statut
    placement_type = models.CharField(_('Type de placement'), max_length=20, choices=PLACEMENT_TYPES)
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Dates
    start_date = models.DateField(_('Date de début'))
    planned_end_date = models.DateField(_('Date de fin prévue'), null=True, blank=True)
    actual_end_date = models.DateField(_('Date de fin réelle'), null=True, blank=True)
    
    # Détails du placement
    placement_reason = models.TextField(_('Raison du placement'))
    special_conditions = models.TextField(_('Conditions spéciales'), blank=True)
    financial_support = models.DecimalField(
        _('Aide financière'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Suivi
    case_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='managed_placements',
        verbose_name=_('Assistant social')
    )
    
    # Évaluation
    success_rating = models.PositiveIntegerField(
        _('Évaluation de réussite'),
        null=True,
        blank=True,
        help_text=_('Note sur 5')  # type: ignore[attr-defined]
    )
    completion_notes = models.TextField(_('Notes de fin'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='created_placements'
    )
    
    class Meta:
        verbose_name = _('Placement')
        verbose_name_plural = _('Placements')
        ordering = ['-start_date']
        unique_together = ['child', 'family', 'start_date']
    
    def __str__(self):
        return f"{self.child.full_name} chez {self.family.family_name}"  # type: ignore[attr-defined]
    
    @property
    def duration_days(self):
        """Durée du placement en jours"""
        end_date = self.actual_end_date or self.planned_end_date
        if end_date:
            return (end_date - self.start_date).days  # type: ignore[attr-defined]
        else:
            from datetime import date
            return (date.today() - self.start_date).days  # type: ignore[attr-defined]

    @property
    def is_active(self):
        """Vérifie si le placement est actif"""
        return self.status == 'active'

class FamilyVisit(models.Model):
    """Visites des familles"""
    
    VISIT_TYPES = [
        ('initial_assessment', _('Évaluation initiale')),
        ('home_study', _('Étude du domicile')),
        ('follow_up', _('Suivi')),
        ('annual_review', _('Révision annuelle')),
        ('emergency', _('Urgence')),
        ('support', _('Soutien')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Planifiée')),
        ('completed', _('Terminée')),
        ('cancelled', _('Annulée')),
        ('rescheduled', _('Reportée')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='visits')
    visitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_visits',
        verbose_name=_('Visiteur')
    )
    
    # Détails de la visite
    visit_type = models.CharField(_('Type de visite'), max_length=20, choices=VISIT_TYPES)
    scheduled_date = models.DateTimeField(_('Date prévue'))
    actual_date = models.DateTimeField(_('Date réelle'), null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(_('Durée (minutes)'), null=True, blank=True)
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Objectifs et résultats
    visit_objectives = models.TextField(_('Objectifs de la visite'), blank=True)
    observations = models.TextField(_('Observations'), blank=True)
    recommendations = models.TextField(_('Recommandations'), blank=True)
    concerns = models.TextField(_('Préoccupations'), blank=True)
    
    # Évaluation
    overall_assessment = models.CharField(
        _('Évaluation globale'),
        max_length=20,
        choices=[
            ('excellent', _('Excellent')),
            ('good', _('Bon')),
            ('satisfactory', _('Satisfaisant')),
            ('needs_improvement', _('À améliorer')),
            ('concerning', _('Préoccupant')),
        ],
        blank=True
    )
    
    # Actions de suivi
    follow_up_required = models.BooleanField(_('Suivi requis'), default=False)  # type: ignore[attr-defined]
    follow_up_date = models.DateField(_('Date de suivi'), null=True, blank=True)
    follow_up_notes = models.TextField(_('Notes de suivi'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Visite de famille')
        verbose_name_plural = _('Visites de familles')
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.get_visit_type_display()} - {self.family.family_name} - {self.scheduled_date.strftime('%d/%m/%Y')}"  # type: ignore[attr-defined]
