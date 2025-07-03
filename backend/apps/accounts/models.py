from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """Modèle utilisateur personnalisé avec rôles et sécurité renforcée"""
    
    ROLE_CHOICES = [
        ('admin', _('Administrateur')),
        ('medecin', _('Médecin')),
        ('soignant', _('Soignant')),
        ('assistant_social', _('Assistant Social')),
        ('logisticien', _('Logisticien')),
        ('donateur', _('Donateur')),
        ('parrain', _('Parrain')),
        ('visiteur', _('Visiteur')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('En attente d\'approbation')),
        ('approved', _('Approuvé')),
        ('rejected', _('Rejeté')),
        ('suspended', _('Suspendu')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email'), unique=True)
    role = models.CharField(_('Rôle'), max_length=20, choices=ROLE_CHOICES, default='visiteur')
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés.")
    )
    phone_number = models.CharField(_('Téléphone'), validators=[phone_regex], max_length=17, blank=True)
    
    # Informations supplémentaires pour l'approbation
    motivation = models.TextField(_('Motivation'), blank=True, help_text=_('Pourquoi souhaitez-vous rejoindre notre organisation?'))
    experience = models.TextField(_('Expérience'), blank=True, help_text=_('Décrivez votre expérience pertinente'))
    specialization = models.CharField(_('Spécialisation'), max_length=200, blank=True, help_text=_('Pour les médecins et soignants'))
    
    # Champs de sécurité
    is_verified = models.BooleanField(_('Email vérifié'), default=False)  # type: ignore[attr-defined]
    failed_login_attempts = models.PositiveIntegerField(_('Tentatives de connexion échouées'), default=0)  # type: ignore[attr-defined]
    last_failed_login = models.DateTimeField(_('Dernière tentative échouée'), null=True, blank=True)
    password_changed_at = models.DateTimeField(_('Mot de passe modifié le'), auto_now_add=True)
    must_change_password = models.BooleanField(_('Doit changer le mot de passe'), default=False)  # type: ignore[attr-defined]
    
    # Champs d'audit
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    approved_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_users')
    approved_at = models.DateTimeField(_('Approuvé le'), null=True, blank=True)
    rejection_reason = models.TextField(_('Raison du rejet'), blank=True)
    
    # Métadonnées
    last_ip_address = models.GenericIPAddressField(_('Dernière adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        permissions = [
            ('can_manage_users', 'Peut gérer les utilisateurs'),
            ('can_view_sensitive_data', 'Peut voir les données sensibles'),
            ('can_export_data', 'Peut exporter les données'),
            ('can_approve_users', 'Peut approuver les utilisateurs'),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def has_role(self, role):
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return self.role == role or self.role == 'admin'
    
    def can_access_child_data(self):
        """Vérifie si l'utilisateur peut accéder aux données des enfants"""
        return self.role in ['admin', 'medecin', 'soignant', 'assistant_social']
    
    def can_manage_inventory(self):
        """Vérifie si l'utilisateur peut gérer l'inventaire"""
        return self.role in ['admin', 'logisticien']
    
    def can_create_child_records(self):
        """Vérifie si l'utilisateur peut créer des dossiers d'enfants"""
        return self.role in ['admin', 'medecin', 'assistant_social']
    
    def is_approved(self):
        """Vérifie si l'utilisateur est approuvé"""
        return self.status == 'approved'

class UserApprovalRequest(models.Model):
    """Demandes d'approbation des utilisateurs"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='approval_request')
    requested_at = models.DateTimeField(_('Demandé le'), auto_now_add=True)
    reviewed_at = models.DateTimeField(_('Examiné le'), null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reviewed_requests')
    admin_notes = models.TextField(_('Notes de l\'administrateur'), blank=True)
    
    class Meta:
        verbose_name = _('Demande d\'approbation')
        verbose_name_plural = _('Demandes d\'approbation')
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Demande de {self.user.get_full_name()} - {self.user.role}"  # type: ignore[attr-defined]

class UserProfile(models.Model):
    """Profil utilisateur étendu"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(_('Biographie'), max_length=500, blank=True)
    date_of_birth = models.DateField(_('Date de naissance'), null=True, blank=True)
    address = models.TextField(_('Adresse'), blank=True)
    emergency_contact = models.CharField(_('Contact d\'urgence'), max_length=100, blank=True)
    emergency_phone = models.CharField(_('Téléphone d\'urgence'), max_length=17, blank=True)
    
    # Préférences
    language = models.CharField(_('Langue'), max_length=10, default='fr')
    timezone = models.CharField(_('Fuseau horaire'), max_length=50, default='Europe/Paris')
    email_notifications = models.BooleanField(_('Notifications par email'), default=True)  # type: ignore[attr-defined]
    sms_notifications = models.BooleanField(_('Notifications par SMS'), default=False)  # type: ignore[attr-defined]
    
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Profil utilisateur')
        verbose_name_plural = _('Profils utilisateur')
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"  # type: ignore[attr-defined]

class LoginAttempt(models.Model):
    """Historique des tentatives de connexion"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(_('Email'))
    ip_address = models.GenericIPAddressField(_('Adresse IP'))
    user_agent = models.TextField(_('User Agent'))
    success = models.BooleanField(_('Succès'))
    timestamp = models.DateTimeField(_('Horodatage'), auto_now_add=True)
    failure_reason = models.CharField(_('Raison de l\'échec'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Tentative de connexion')
        verbose_name_plural = _('Tentatives de connexion')
        ordering = ['-timestamp']
    
    def __str__(self):
        status = "Réussie" if self.success else "Échouée"
        return f"{self.email} - {status} - {self.timestamp}"

class PasswordHistory(models.Model):
    """Historique des mots de passe pour éviter la réutilisation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(_('Hash du mot de passe'), max_length=128)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Historique des mots de passe')
        verbose_name_plural = _('Historiques des mots de passe')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Mot de passe de {self.user.get_full_name()} - {self.created_at}"  # type: ignore[attr-defined]
