from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from decimal import Decimal

class Donor(models.Model):
    """Modèle pour les donateurs"""
    
    DONOR_TYPES = [
        ('individual', _('Particulier')),
        ('company', _('Entreprise')),
        ('foundation', _('Fondation')),
        ('government', _('Gouvernement')),
        ('ngo', _('ONG')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='donor_profile'
    )
    
    # Informations de base
    name = models.CharField(_('Nom'), max_length=200)
    donor_type = models.CharField(_('Type de donateur'), max_length=20, choices=DONOR_TYPES, default='individual')
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Téléphone'), max_length=20, blank=True)
    
    # Adresse
    address_line1 = models.CharField(_('Adresse ligne 1'), max_length=200, blank=True)
    address_line2 = models.CharField(_('Adresse ligne 2'), max_length=200, blank=True)
    city = models.CharField(_('Ville'), max_length=100, blank=True)
    postal_code = models.CharField(_('Code postal'), max_length=20, blank=True)
    country = models.CharField(_('Pays'), max_length=100, default='France')
    
    # Informations entreprise (si applicable)
    company_registration = models.CharField(_('Numéro d\'enregistrement'), max_length=50, blank=True)
    tax_id = models.CharField(_('Numéro fiscal'), max_length=50, blank=True)
    
    # Préférences
    preferred_contact_method = models.CharField(
        _('Méthode de contact préférée'),
        max_length=20,
        choices=[('email', 'Email'), ('phone', 'Téléphone'), ('mail', 'Courrier')],
        default='email'
    )
    newsletter_subscription = models.BooleanField(_('Abonnement newsletter'), default=True)  # type: ignore[attr-defined]
    anonymous_donations = models.BooleanField(_('Dons anonymes'), default=False)  # type: ignore[attr-defined]
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    is_active = models.BooleanField(_('Actif'), default=True)  # type: ignore[attr-defined]
    
    class Meta:
        verbose_name = _('Donateur')
        verbose_name_plural = _('Donateurs')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_donations(self):
        """Montant total des dons"""
        return self.donations.aggregate(  # type: ignore[attr-defined]
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def donation_count(self):
        """Nombre de dons"""
        return self.donations.count()  # type: ignore[attr-defined]

class Donation(models.Model):
    """Modèle pour les dons"""
    
    DONATION_TYPES = [
        ('money', _('Argent')),
        ('food', _('Nourriture')),
        ('clothing', _('Vêtements')),
        ('medicine', _('Médicaments')),
        ('toys', _('Jouets')),
        ('books', _('Livres')),
        ('furniture', _('Mobilier')),
        ('electronics', _('Électronique')),
        ('other', _('Autre')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('confirmed', _('Confirmé')),
        ('received', _('Reçu')),
        ('distributed', _('Distribué')),
        ('cancelled', _('Annulé')),
    ]
    
    PAYMENT_METHODS = [
        ('cash', _('Espèces')),
        ('check', _('Chèque')),
        ('bank_transfer', _('Virement bancaire')),
        ('credit_card', _('Carte de crédit')),
        ('paypal', _('PayPal')),
        ('other', _('Autre')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    
    # Informations du don
    donation_type = models.CharField(_('Type de don'), max_length=20, choices=DONATION_TYPES)
    amount = models.DecimalField(
        _('Montant/Valeur estimée'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(_('Devise'), max_length=3, default='EUR')
    
    # Description et détails
    description = models.TextField(_('Description'), blank=True)
    quantity = models.PositiveIntegerField(_('Quantité'), default=1)  # type: ignore[attr-defined]
    unit = models.CharField(_('Unité'), max_length=50, blank=True)
    
    # Dates
    donation_date = models.DateTimeField(_('Date du don'))
    received_date = models.DateTimeField(_('Date de réception'), null=True, blank=True)
    
    # Statut et suivi
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(_('Méthode de paiement'), max_length=20, choices=PAYMENT_METHODS, blank=True)
    reference_number = models.CharField(_('Numéro de référence'), max_length=100, blank=True)
    
    # Reçu fiscal
    tax_receipt_requested = models.BooleanField(_('Reçu fiscal demandé'), default=False)  # type: ignore[attr-defined]
    tax_receipt_sent = models.BooleanField(_('Reçu fiscal envoyé'), default=False)  # type: ignore[attr-defined]
    tax_receipt_date = models.DateTimeField(_('Date d\'envoi du reçu'), null=True, blank=True)
    
    # Affectation
    designated_for = models.CharField(_('Destiné à'), max_length=200, blank=True)
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='donations', verbose_name=_('Enfant bénéficiaire'))
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_donations', verbose_name=_('Enregistré par'))
    
    # Notes internes
    internal_notes = models.TextField(_('Notes internes'), blank=True)
    
    class Meta:
        verbose_name = _('Don')
        verbose_name_plural = _('Dons')
        ordering = ['-donation_date']
        permissions = [
            ('can_approve_donations', 'Peut approuver les dons'),
            ('can_generate_tax_receipts', 'Peut générer les reçus fiscaux'),
        ]
    
    def __str__(self):
        return f"{self.donor.name} - {self.get_donation_type_display()} - {self.amount} {self.currency}"  # type: ignore[attr-defined]
    
    def save(self, *args, **kwargs):
        """Génère un numéro de référence automatique"""
        if not self.reference_number:
            from datetime import datetime
            self.reference_number = f"DON-{datetime.now().strftime('%Y%m%d')}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

class DonationCampaign(models.Model):
    """Modèle pour les campagnes de dons"""
    
    CAMPAIGN_TYPES = [
        ('general', _('Général')),
        ('emergency', _('Urgence')),
        ('education', _('Éducation')),
        ('medical', _('Médical')),
        ('infrastructure', _('Infrastructure')),
        ('seasonal', _('Saisonnier')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('active', _('Active')),
        ('paused', _('En pause')),
        ('completed', _('Terminée')),
        ('cancelled', _('Annulée')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom de la campagne'), max_length=200)
    description = models.TextField(_('Description'))
    campaign_type = models.CharField(_('Type de campagne'), max_length=20, choices=CAMPAIGN_TYPES)
    
    # Objectifs
    target_amount = models.DecimalField(
        _('Objectif financier'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    current_amount = models.DecimalField(
        _('Montant actuel'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Dates
    start_date = models.DateTimeField(_('Date de début'))
    end_date = models.DateTimeField(_('Date de fin'))
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Médias
    image = models.ImageField(_('Image'), upload_to='campaigns/', null=True, blank=True)
    video_url = models.URLField(_('URL vidéo'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_campaigns')
    
    class Meta:
        verbose_name = _('Campagne de dons')
        verbose_name_plural = _('Campagnes de dons')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def progress_percentage(self):
        """Pourcentage de progression"""
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)  # type: ignore[attr-defined]
        return 0
    
    @property
    def is_active(self):
        """Vérifie si la campagne est active"""
        from django.utils import timezone
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_date <= now <= self.end_date)

class RecurringDonation(models.Model):
    """Modèle pour les dons récurrents"""
    
    FREQUENCY_CHOICES = [
        ('weekly', _('Hebdomadaire')),
        ('monthly', _('Mensuel')),
        ('quarterly', _('Trimestriel')),
        ('yearly', _('Annuel')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Actif')),
        ('paused', _('En pause')),
        ('cancelled', _('Annulé')),
        ('completed', _('Terminé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='recurring_donations')
    
    # Configuration du don récurrent
    amount = models.DecimalField(
        _('Montant'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    frequency = models.CharField(_('Fréquence'), max_length=20, choices=FREQUENCY_CHOICES)
    
    # Dates
    start_date = models.DateField(_('Date de début'))
    end_date = models.DateField(_('Date de fin'), null=True, blank=True)
    next_payment_date = models.DateField(_('Prochaine date de paiement'))
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Informations de paiement
    payment_method = models.CharField(_('Méthode de paiement'), max_length=20, choices=Donation.PAYMENT_METHODS)
    payment_reference = models.CharField(_('Référence de paiement'), max_length=200, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Don récurrent')
        verbose_name_plural = _('Dons récurrents')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.frequency} - {self.amount} {self.currency} - {self.get_frequency_display()}"  # type: ignore[attr-defined]
    
    def calculate_next_payment_date(self):
        """Calcule la prochaine date de paiement"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        if self.frequency == 'weekly':
            return self.next_payment_date + timedelta(weeks=1)  # type: ignore[attr-defined]
        elif self.frequency == 'monthly':
            return self.next_payment_date + relativedelta(months=1)  # type: ignore[attr-defined]
        elif self.frequency == 'quarterly':
            return self.next_payment_date + relativedelta(months=3)  # type: ignore[attr-defined]
        elif self.frequency == 'yearly':
            return self.next_payment_date + relativedelta(years=1)  # type: ignore[attr-defined]
        
        return self.next_payment_date
