from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from datetime import date

class Child(models.Model):
    """Modèle pour les enfants de l'orphelinat"""
    
    GENDER_CHOICES = [
        ('M', _('Masculin')),
        ('F', _('Féminin')),
    ]
    
    STATUS_CHOICES = [
        ('a_parrainer', _('À parrainer')),
        ('parraine', _('Parrainé')),
        ('adopte', _('Adopté')),
        ('en_attente', _('En attente')),
        ('sorti', _('Sorti de l\'établissement')),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('unknown', _('Inconnu')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations personnelles
    first_name = models.CharField(_('Prénom'), max_length=100)
    last_name = models.CharField(_('Nom de famille'), max_length=100)
    nickname = models.CharField(_('Surnom'), max_length=50, blank=True)
    date_of_birth = models.DateField(_('Date de naissance'))
    place_of_birth = models.CharField(_('Lieu de naissance'), max_length=200, blank=True)
    gender = models.CharField(_('Sexe'), max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(_('Nationalité'), max_length=100, default='Française')
    
    # Informations d'arrivée
    arrival_date = models.DateField(_('Date d\'arrivée'))
    arrival_reason = models.TextField(_('Raison de l\'arrivée'), blank=True)
    arrival_circumstances = models.TextField(_('Circonstances d\'arrivée'), blank=True)
    
    # Statut et suivi
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='a_parrainer')
    case_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='case_children',
        limit_choices_to={'role__in': ['assistant_social', 'admin']},
        verbose_name=_('Assistant social responsable')
    )
    
    # Informations médicales
    blood_type = models.CharField(_('Groupe sanguin'), max_length=10, choices=BLOOD_TYPE_CHOICES, default='unknown')
    allergies = models.TextField(_('Allergies'), blank=True)
    medical_conditions = models.TextField(_('Conditions médicales'), blank=True)
    medications = models.TextField(_('Médicaments'), blank=True)
    vaccination_status = models.TextField(_('Statut vaccinal'), blank=True)
    last_medical_checkup = models.DateField(_('Dernière visite médicale'), null=True, blank=True)
    
    # Informations éducatives
    education_level = models.CharField(_('Niveau d\'éducation'), max_length=100, blank=True)
    school = models.CharField(_('École'), max_length=200, blank=True)
    special_needs = models.TextField(_('Besoins spéciaux'), blank=True)
    languages_spoken = models.CharField(_('Langues parlées'), max_length=200, default='Français')
    
    # Informations familiales
    family_background = models.TextField(_('Contexte familial'), blank=True)
    emergency_contact_name = models.CharField(_('Contact d\'urgence - Nom'), max_length=200, blank=True)
    emergency_contact_phone = models.CharField(_('Contact d\'urgence - Téléphone'), max_length=20, blank=True)
    emergency_contact_relation = models.CharField(_('Contact d\'urgence - Relation'), max_length=100, blank=True)
    
    # Documents et photos
    photo = models.ImageField(_('Photo'), upload_to='children/photos/', null=True, blank=True)
    birth_certificate = models.FileField(_('Acte de naissance'), upload_to='children/documents/', null=True, blank=True)
    medical_records = models.FileField(_('Dossier médical'), upload_to='children/medical/', null=True, blank=True)
    
    # Informations de parrainage/adoption
    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sponsored_children',
        limit_choices_to={'role__in': ['parrain', 'donateur']},
        verbose_name=_('Parrain/Marraine')
    )
    sponsor_start_date = models.DateField(_('Date de début du parrainage'), null=True, blank=True)
    adoption_family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        related_name='adopted_children',
        verbose_name=_('Famille adoptive')
    )
    adoption_date = models.DateField(_('Date d\'adoption'), null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_children',
        verbose_name=_('Créé par')
    )
    
    # Champs de confidentialité
    is_confidential = models.BooleanField(_('Dossier confidentiel'), default=False)  # type: ignore[attr-defined]
    confidentiality_reason = models.TextField(_('Raison de la confidentialité'), blank=True)
    
    class Meta:
        verbose_name = _('Enfant')
        verbose_name_plural = _('Enfants')
        ordering = ['last_name', 'first_name']
        permissions = [
            ('view_confidential_child', 'Peut voir les dossiers confidentiels'),
            ('export_child_data', 'Peut exporter les données des enfants'),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Nom complet de l'enfant"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcule l'âge de l'enfant"""
        today = date.today()
        return today.year - self.date_of_birth.year - (  # type: ignore[attr-defined]
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)  # type: ignore[attr-defined]
        )
    
    @property
    def days_in_care(self):
        """Nombre de jours dans l'établissement"""
        return (date.today() - self.arrival_date).days  # type: ignore[attr-defined]
    
    def get_anonymized_data(self):
        """Retourne les données anonymisées pour l'affichage public"""
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'age': self.age,
            'gender': self.gender,
            'status': self.status,
            'photo': self.photo.url if self.photo else None,  # type: ignore[attr-defined]
            'arrival_date': self.arrival_date,
        }
    
    def can_be_viewed_by(self, user):
        """Vérifie si un utilisateur peut voir ce dossier"""
        if user.role == 'admin':
            return True
        
        if self.is_confidential and not user.has_perm('children.view_confidential_child'):
            return False
        
        if user.role in ['assistant_social', 'soignant']:
            return True
        
        if user.role == 'parrain' and self.sponsor == user:
            return True
        
        return False

class ChildNote(models.Model):
    """Notes sur les enfants"""
    
    NOTE_TYPES = [
        ('medical', _('Médical')),
        ('behavioral', _('Comportemental')),
        ('educational', _('Éducatif')),
        ('social', _('Social')),
        ('administrative', _('Administratif')),
        ('other', _('Autre')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note_type = models.CharField(_('Type de note'), max_length=20, choices=NOTE_TYPES)
    title = models.CharField(_('Titre'), max_length=200)
    content = models.TextField(_('Contenu'))
    is_confidential = models.BooleanField(_('Confidentiel'), default=False)  # type: ignore[attr-defined]
    
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Note sur enfant')
        verbose_name_plural = _('Notes sur enfants')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.child.full_name}"  # type: ignore[attr-defined]

class ChildDocument(models.Model):
    """Documents liés aux enfants"""
    
    DOCUMENT_TYPES = [
        ('birth_certificate', _('Acte de naissance')),
        ('medical_record', _('Dossier médical')),
        ('school_report', _('Bulletin scolaire')),
        ('photo', _('Photo')),
        ('legal_document', _('Document légal')),
        ('other', _('Autre')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(_('Type de document'), max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    file = models.FileField(_('Fichier'), upload_to='children/documents/')
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(_('Téléchargé le'), auto_now_add=True)
    
    is_confidential = models.BooleanField(_('Confidentiel'), default=False)  # type: ignore[attr-defined]
    
    class Meta:
        verbose_name = _('Document enfant')
        verbose_name_plural = _('Documents enfants')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.child.full_name}"  # type: ignore[attr-defined]

class MedicalRecord(models.Model):
    """Dossiers médicaux des enfants"""
    
    VISIT_TYPES = [
        ('routine', _('Visite de routine')),
        ('emergency', _('Urgence')),
        ('specialist', _('Spécialiste')),
        ('vaccination', _('Vaccination')),
        ('dental', _('Dentaire')),
        ('psychological', _('Psychologique')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='medical_records_set')
    visit_date = models.DateTimeField(_('Date de la visite'))
    visit_type = models.CharField(_('Type de visite'), max_length=20, choices=VISIT_TYPES)
    doctor_name = models.CharField(_('Nom du médecin'), max_length=200)
    clinic_hospital = models.CharField(_('Clinique/Hôpital'), max_length=200, blank=True)
    
    symptoms = models.TextField(_('Symptômes'), blank=True)
    diagnosis = models.TextField(_('Diagnostic'), blank=True)
    treatment = models.TextField(_('Traitement'), blank=True)
    medications_prescribed = models.TextField(_('Médicaments prescrits'), blank=True)
    follow_up_required = models.BooleanField(_('Suivi requis'), default=False)  # type: ignore[attr-defined]
    follow_up_date = models.DateField(_('Date de suivi'), null=True, blank=True)
    
    height = models.DecimalField(_('Taille (cm)'), max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(_('Poids (kg)'), max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(_('Température (°C)'), max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure = models.CharField(_('Tension artérielle'), max_length=20, blank=True)
    
    notes = models.TextField(_('Notes'), blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Dossier médical')
        verbose_name_plural = _('Dossiers médicaux')
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.child.full_name} - {self.visit_date.strftime('%d/%m/%Y')} - {self.get_visit_type_display()}"  # type: ignore[attr-defined]
