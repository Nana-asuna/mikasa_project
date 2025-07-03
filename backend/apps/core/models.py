from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from cryptography.fernet import Fernet
import uuid
import json
import base64

class EncryptedField(models.TextField):
    """Champ personnalisé pour chiffrer les données sensibles"""
    
    def __init__(self, *args, **kwargs):
        self.encryption_key = kwargs.pop('encryption_key', None)
        super().__init__(*args, **kwargs)
    
    def get_encryption_key(self):
        """Récupère la clé de chiffrement"""
        if self.encryption_key:
            return self.encryption_key
        return settings.FIELD_ENCRYPTION_KEY.encode()
    
    def encrypt_value(self, value):
        """Chiffre une valeur"""
        if not value:
            return value
        
        fernet = Fernet(base64.urlsafe_b64encode(self.get_encryption_key()[:32]))
        encrypted_value = fernet.encrypt(str(value).encode())
        return base64.urlsafe_b64encode(encrypted_value).decode()
    
    def decrypt_value(self, value):
        """Déchiffre une valeur"""
        if not value:
            return value
        
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.get_encryption_key()[:32]))
            encrypted_value = base64.urlsafe_b64decode(value.encode())
            decrypted_value = fernet.decrypt(encrypted_value)
            return decrypted_value.decode()
        except Exception:
            return value  # Retourne la valeur non chiffrée si erreur
    
    def from_db_value(self, value, expression, connection):
        """Déchiffre lors de la lecture depuis la DB"""
        return self.decrypt_value(value)
    
    def to_python(self, value):
        """Convertit la valeur en Python"""
        return self.decrypt_value(value)
    
    def get_prep_value(self, value):
        """Chiffre avant sauvegarde en DB"""
        return self.encrypt_value(value)

class AuditTrail(models.Model):
    """Piste d'audit pour toutes les actions sensibles"""
    
    ACTION_CHOICES = [
        ('create', _('Création')),
        ('read', _('Lecture')),
        ('update', _('Modification')),
        ('delete', _('Suppression')),
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('export', _('Export')),
        ('import', _('Import')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Utilisateur et session
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_user',
        null=True,
        blank=True
    )
    session_key = models.CharField(_('Clé de session'), max_length=40, blank=True)
    
    # Action
    action = models.CharField(_('Action'), max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(_('Modèle'), max_length=100)
    object_id = models.CharField(_('ID Objet'), max_length=100, blank=True)
    object_repr = models.CharField(_('Représentation'), max_length=200, blank=True)
    
    # Détails
    changes = models.JSONField(_('Modifications'), default=dict, blank=True)
    additional_data = models.JSONField(_('Données supplémentaires'), default=dict, blank=True)
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(_('Adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    request_path = models.CharField(_('Chemin de requête'), max_length=500, blank=True)
    request_method = models.CharField(_('Méthode HTTP'), max_length=10, blank=True)
    
    # Horodatage
    timestamp = models.DateTimeField(_('Horodatage'), auto_now_add=True)
    
    # Sécurité
    checksum = models.CharField(_('Somme de contrôle'), max_length=64, blank=True)
    
    class Meta:
        verbose_name = _('Piste d\'audit')
        verbose_name_plural = _('Pistes d\'audit')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def save(self, *args, **kwargs):
        """Calcule la somme de contrôle avant sauvegarde"""
        if not self.checksum:
            import hashlib
            data = f"{self.user.id}{self.action}{self.model_name}{self.timestamp}"  # type: ignore[attr-defined]
            self.checksum = hashlib.sha256(data.encode()).hexdigest()
        super().save(*args, **kwargs)

class GDPRConsent(models.Model):
    """Gestion des consentements RGPD"""
    
    CONSENT_TYPES = [
        ('data_processing', _('Traitement des données')),
        ('medical_data', _('Données médicales')),
        ('photo_usage', _('Utilisation des photos')),
        ('communication', _('Communications')),
        ('research', _('Recherche')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Sujet du consentement
    child = models.ForeignKey(
        'children.Child',
        on_delete=models.CASCADE,
        related_name='core_child',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_user',
        null=True,
        blank=True
    )
    
    # Détails du consentement
    consent_type = models.CharField(_('Type de consentement'), max_length=30, choices=CONSENT_TYPES)
    purpose = models.TextField(_('Finalité'))
    legal_basis = models.CharField(_('Base légale'), max_length=200)
    
    # Statut
    granted = models.BooleanField(_('Accordé'), default=False)  # type: ignore[attr-defined]
    granted_at = models.DateTimeField(_('Accordé le'), null=True, blank=True)
    withdrawn_at = models.DateTimeField(_('Retiré le'), null=True, blank=True)
    
    # Métadonnées
    version = models.CharField(_('Version'), max_length=10, default='1.0')
    ip_address = models.GenericIPAddressField(_('Adresse IP'))
    user_agent = models.TextField(_('User Agent'))
    
    # Horodatage
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Consentement RGPD')
        verbose_name_plural = _('Consentements RGPD')
        unique_together = ['child', 'user', 'consent_type']

class DataRetention(models.Model):
    """Gestion de la rétention des données"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Données concernées
    model_name = models.CharField(_('Modèle'), max_length=100)
    object_id = models.CharField(_('ID Objet'), max_length=100)
    
    # Politique de rétention
    retention_period_days = models.PositiveIntegerField(_('Période de rétention (jours)'))
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expire le'))
    
    # Statut
    is_anonymized = models.BooleanField(_('Anonymisé'), default=False)  # type: ignore[attr-defined]
    anonymized_at = models.DateTimeField(_('Anonymisé le'), null=True, blank=True)
    is_deleted = models.BooleanField(_('Supprimé'), default=False)  # type: ignore[attr-defined]
    deleted_at = models.DateTimeField(_('Supprimé le'), null=True, blank=True)
    
    # Raison de conservation
    retention_reason = models.TextField(_('Raison de conservation'), blank=True)
    legal_hold = models.BooleanField(_('Conservation légale'), default=False)  # type: ignore[attr-defined]
    
    class Meta:
        verbose_name = _('Rétention de données')
        verbose_name_plural = _('Rétentions de données')
        unique_together = ['model_name', 'object_id']

class SecurityIncident(models.Model):
    """Incidents de sécurité"""
    
    SEVERITY_CHOICES = [
        ('low', _('Faible')),
        ('medium', _('Moyen')),
        ('high', _('Élevé')),
        ('critical', _('Critique')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Ouvert')),
        ('investigating', _('En cours d\'investigation')),
        ('resolved', _('Résolu')),
        ('closed', _('Fermé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Détails de l'incident
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    severity = models.CharField(_('Gravité'), max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(_('Adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    request_data = models.JSONField(_('Données de requête'), default=dict, blank=True)
    
    # Utilisateur concerné
    affected_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_affected',
        null=True,
        blank=True
    )
    
    # Gestion
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_assigned',
        null=True,
        blank=True
    )
    
    # Actions prises
    actions_taken = models.TextField(_('Actions prises'), blank=True)
    resolution_notes = models.TextField(_('Notes de résolution'), blank=True)
    
    # Horodatage
    detected_at = models.DateTimeField(_('Détecté le'), auto_now_add=True)
    resolved_at = models.DateTimeField(_('Résolu le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Incident de sécurité')
        verbose_name_plural = _('Incidents de sécurité')
        ordering = ['-detected_at']
