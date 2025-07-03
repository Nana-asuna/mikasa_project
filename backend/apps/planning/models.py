from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from datetime import datetime, timedelta

class Event(models.Model):
    """Événements du planning"""
    
    EVENT_TYPES = [
        ('medical_visit', _('Visite médicale')),
        ('activity', _('Activité')),
        ('education', _('Éducation')),
        ('recreation', _('Récréation')),
        ('meal', _('Repas')),
        ('therapy', _('Thérapie')),
        ('meeting', _('Réunion')),
        ('appointment', _('Rendez-vous')),
        ('maintenance', _('Maintenance')),
        ('other', _('Autre')),
    ]
    
    PRIORITY_LEVELS = [
        ('low', _('Faible')),
        ('medium', _('Moyenne')),
        ('high', _('Élevée')),
        ('urgent', _('Urgente')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Planifié')),
        ('confirmed', _('Confirmé')),
        ('in_progress', _('En cours')),
        ('completed', _('Terminé')),
        ('cancelled', _('Annulé')),
        ('postponed', _('Reporté')),
    ]
    
    RECURRENCE_TYPES = [
        ('none', _('Aucune')),
        ('daily', _('Quotidienne')),
        ('weekly', _('Hebdomadaire')),
        ('monthly', _('Mensuelle')),
        ('yearly', _('Annuelle')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    event_type = models.CharField(_('Type d\'événement'), max_length=20, choices=EVENT_TYPES)
    
    # Dates et heures
    start_datetime = models.DateTimeField(_('Date et heure de début'))
    end_datetime = models.DateTimeField(_('Date et heure de fin'))
    all_day = models.BooleanField(_('Toute la journée'), default=False)  # type: ignore[attr-defined]
    
    # Localisation
    location = models.CharField(_('Lieu'), max_length=200, blank=True)
    room = models.CharField(_('Salle'), max_length=100, blank=True)
    
    # Participants
    children = models.ManyToManyField(
        'children.Child',
        blank=True,
        related_name='events',
        verbose_name=_('Enfants participants')
    )
    staff_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='assigned_events',
        verbose_name=_('Personnel assigné')
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name=_('Organisateur')
    )
    
    # Priorité et statut
    priority = models.CharField(_('Priorité'), max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Récurrence
    recurrence_type = models.CharField(_('Type de récurrence'), max_length=10, choices=RECURRENCE_TYPES, default='none')
    recurrence_end_date = models.DateField(_('Fin de récurrence'), null=True, blank=True)
    parent_event = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_events',
        verbose_name=_('Événement parent')
    )
    
    # Rappels
    reminder_minutes = models.PositiveIntegerField(
        _('Rappel (minutes avant)'),
        null=True,
        blank=True,
        help_text=_('Nombre de minutes avant l\'événement pour envoyer un rappel')  # type: ignore[attr-defined]
    )
    reminder_sent = models.BooleanField(_('Rappel envoyé'), default=False)  # type: ignore[attr-defined]
    
    # Ressources nécessaires
    required_materials = models.TextField(_('Matériel nécessaire'), blank=True)
    estimated_cost = models.DecimalField(
        _('Coût estimé'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Notes et résultats
    preparation_notes = models.TextField(_('Notes de préparation'), blank=True)
    completion_notes = models.TextField(_('Notes de fin'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events',
        verbose_name=_('Créé par')
    )
    
    class Meta:
        verbose_name = _('Événement')
        verbose_name_plural = _('Événements')
        ordering = ['start_datetime']
        permissions = [
            ('can_manage_all_events', 'Peut gérer tous les événements'),
            ('can_view_all_events', 'Peut voir tous les événements'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"  # type: ignore[attr-defined]
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        if self.end_datetime <= self.start_datetime:
            raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))
        
        if self.recurrence_type != 'none' and not self.recurrence_end_date:
            raise ValidationError(_('Une date de fin de récurrence est requise pour les événements récurrents.'))
    
    @property
    def duration(self):
        """Durée de l'événement"""
        return self.end_datetime - self.start_datetime  # type: ignore[attr-defined]
    
    @property
    def is_past(self):
        """Vérifie si l'événement est passé"""
        from django.utils import timezone
        return self.end_datetime < timezone.now()
    
    @property
    def is_today(self):
        """Vérifie si l'événement est aujourd'hui"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_datetime.date() == today  # type: ignore[attr-defined]
    
    def can_be_modified_by(self, user):
        """Vérifie si un utilisateur peut modifier cet événement"""
        if user.role == 'admin':
            return True
        if user == self.organizer:
            return True
        if user.has_perm('planning.can_manage_all_events'):
            return True
        return False

class Schedule(models.Model):
    """Planning personnel"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    
    # Préférences de planning
    work_start_time = models.TimeField(_('Heure de début de travail'), default='08:00')
    work_end_time = models.TimeField(_('Heure de fin de travail'), default='17:00')
    lunch_break_duration = models.PositiveIntegerField(_('Durée pause déjeuner (minutes)'), default=60)  # type: ignore[attr-defined]
    
    # Jours de travail
    monday = models.BooleanField(_('Lundi'), default=True)  # type: ignore[attr-defined]
    tuesday = models.BooleanField(_('Mardi'), default=True)  # type: ignore[attr-defined]
    wednesday = models.BooleanField(_('Mercredi'), default=True)  # type: ignore[attr-defined]
    thursday = models.BooleanField(_('Jeudi'), default=True)  # type: ignore[attr-defined]
    friday = models.BooleanField(_('Vendredi'), default=True)  # type: ignore[attr-defined]
    saturday = models.BooleanField(_('Samedi'), default=False)  # type: ignore[attr-defined]
    sunday = models.BooleanField(_('Dimanche'), default=False)  # type: ignore[attr-defined]
    
    # Notifications
    email_reminders = models.BooleanField(_('Rappels par email'), default=True)  # type: ignore[attr-defined]
    sms_reminders = models.BooleanField(_('Rappels par SMS'), default=False)  # type: ignore[attr-defined]
    reminder_advance_minutes = models.PositiveIntegerField(_('Avance des rappels (minutes)'), default=30)  # type: ignore[attr-defined]
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Planning')
        verbose_name_plural = _('Plannings')
    
    def __str__(self):
        return f"Planning de {self.user.get_full_name()}"  # type: ignore[attr-defined]
    
    @property
    def working_days(self):
        """Liste des jours de travail"""
        days = []
        if self.monday: days.append(0)
        if self.tuesday: days.append(1)
        if self.wednesday: days.append(2)
        if self.thursday: days.append(3)
        if self.friday: days.append(4)
        if self.saturday: days.append(5)
        if self.sunday: days.append(6)
        return days

class Availability(models.Model):
    """Disponibilités du personnel"""
    
    AVAILABILITY_TYPES = [
        ('available', _('Disponible')),
        ('busy', _('Occupé')),
        ('vacation', _('Congés')),
        ('sick_leave', _('Arrêt maladie')),
        ('training', _('Formation')),
        ('meeting', _('Réunion')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    
    # Période
    start_datetime = models.DateTimeField(_('Début'))
    end_datetime = models.DateTimeField(_('Fin'))
    
    # Type et détails
    availability_type = models.CharField(_('Type'), max_length=20, choices=AVAILABILITY_TYPES)
    title = models.CharField(_('Titre'), max_length=200, blank=True)
    description = models.TextField(_('Description'), blank=True)
    
    # Récurrence
    is_recurring = models.BooleanField(_('Récurrent'), default=False)  # type: ignore[attr-defined]
    recurrence_pattern = models.CharField(_('Motif de récurrence'), max_length=100, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Disponibilité')
        verbose_name_plural = _('Disponibilités')
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_availability_type_display()}"  # type: ignore[attr-defined]
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        if self.end_datetime <= self.start_datetime:
            raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))

class Task(models.Model):
    """Tâches à accomplir"""
    
    PRIORITY_LEVELS = [
        ('low', _('Faible')),
        ('medium', _('Moyenne')),
        ('high', _('Élevée')),
        ('urgent', _('Urgente')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('in_progress', _('En cours')),
        ('completed', _('Terminée')),
        ('cancelled', _('Annulée')),
        ('on_hold', _('En pause')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    title = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    
    # Attribution
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name=_('Assigné à')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name=_('Créé par')
    )
    
    # Dates
    due_date = models.DateTimeField(_('Date d\'échéance'), null=True, blank=True)
    completed_date = models.DateTimeField(_('Date de completion'), null=True, blank=True)
    
    # Priorité et statut
    priority = models.CharField(_('Priorité'), max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Progression
    progress_percentage = models.PositiveIntegerField(
        _('Pourcentage de progression'),
        default=0,  # type: ignore[attr-defined]
        validators=[MinValueValidator(0), MaxValueValidator(100)]  # type: ignore[attr-defined]
    )
    
    # Relations
    related_child = models.ForeignKey(
        'children.Child',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='related_tasks',
        verbose_name=_('Enfant concerné')
    )
    related_event = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='related_events',
        verbose_name=_('Événement lié')
    )
    
    # Estimation et suivi
    estimated_hours = models.DecimalField(
        _('Heures estimées'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_hours = models.DecimalField(
        _('Heures réelles'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    completion_notes = models.TextField(_('Notes de completion'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Tâche')
        verbose_name_plural = _('Tâches')
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """Vérifie si la tâche est en retard"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return self.due_date < timezone.now()
        return False
    
    @property
    def days_until_due(self):
        """Nombre de jours avant l'échéance"""
        if self.due_date:
            from django.utils import timezone
            delta = self.due_date.date() - timezone.now().date()  # type: ignore[attr-defined]
            return delta.days
        return None

class Shift(models.Model):
    """Équipes de travail"""
    
    SHIFT_TYPES = [
        ('morning', _('Matin')),
        ('afternoon', _('Après-midi')),
        ('evening', _('Soir')),
        ('night', _('Nuit')),
        ('full_day', _('Journée complète')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom de l\'équipe'), max_length=100)
    shift_type = models.CharField(_('Type d\'équipe'), max_length=20, choices=SHIFT_TYPES)
    
    # Horaires
    start_time = models.TimeField(_('Heure de début'))
    end_time = models.TimeField(_('Heure de fin'))
    
    # Date
    date = models.DateField(_('Date'))
    
    # Personnel
    staff_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ShiftAssignment',
        related_name='shifts',
        verbose_name=_('Personnel')
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='supervised_tasks',
        verbose_name=_('Superviseur')
    )
    
    # Capacité
    minimum_staff = models.PositiveIntegerField(_('Personnel minimum'), default=1)  # type: ignore[attr-defined]
    maximum_staff = models.PositiveIntegerField(_('Personnel maximum'), default=10)  # type: ignore[attr-defined]
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_shifts'
    )
    
    class Meta:
        verbose_name = _('Équipe')
        verbose_name_plural = _('Équipes')
        ordering = ['date', 'start_time']
        unique_together = ['date', 'shift_type']
    
    def __str__(self):
        return f"{self.name} - {self.date} ({self.start_time}-{self.end_time})"
    
    @property
    def current_staff_count(self):
        """Nombre actuel de personnel assigné"""
        return self.staff_members.count()  # type: ignore[attr-defined]
    
    @property
    def is_fully_staffed(self):
        """Vérifie si l'équipe est complète"""
        return self.current_staff_count >= self.minimum_staff  # type: ignore[attr-defined]

class ShiftAssignment(models.Model):
    """Attribution d'équipes au personnel"""
    
    ASSIGNMENT_STATUS = [
        ('assigned', _('Assigné')),
        ('confirmed', _('Confirmé')),
        ('completed', _('Terminé')),
        ('absent', _('Absent')),
        ('cancelled', _('Annulé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=ASSIGNMENT_STATUS, default='assigned')
    
    # Heures réelles
    actual_start_time = models.TimeField(_('Heure de début réelle'), null=True, blank=True)
    actual_end_time = models.TimeField(_('Heure de fin réelle'), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Attribution d\'équipe')
        verbose_name_plural = _('Attributions d\'équipes')
        unique_together = ['shift', 'staff_member']
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.shift.name}"  # type: ignore[attr-defined]
