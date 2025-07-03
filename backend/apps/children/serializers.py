from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Child, ChildNote, ChildDocument, MedicalRecord
from apps.accounts.serializers import UserSerializer

class ChildSerializer(serializers.ModelSerializer):
    """Serializer pour les enfants"""
    age = serializers.ReadOnlyField()
    days_in_care = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    case_worker_name = serializers.CharField(source='case_worker.get_full_name', read_only=True)
    sponsor_name = serializers.CharField(source='sponsor.get_full_name', read_only=True)
    
    class Meta:
        model = Child
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def validate_date_of_birth(self, value):
        """Validation de la date de naissance"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError(_("La date de naissance ne peut pas être dans le futur."))
        
        # Vérifier que l'enfant n'est pas trop âgé (par exemple, plus de 18 ans)
        age = date.today().year - value.year
        if age > 18:
            raise serializers.ValidationError(_("L'enfant ne peut pas avoir plus de 18 ans."))
        
        return value
    
    def validate_arrival_date(self, value):
        """Validation de la date d'arrivée"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError(_("La date d'arrivée ne peut pas être dans le futur."))
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        if 'date_of_birth' in attrs and 'arrival_date' in attrs:
            if attrs['arrival_date'] < attrs['date_of_birth']:
                raise serializers.ValidationError(_("La date d'arrivée ne peut pas être antérieure à la date de naissance."))
        
        return attrs
    
    def to_representation(self, instance):
        """Personnalise la représentation selon les permissions"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and request.user:
            # Si l'utilisateur est un visiteur, anonymiser certaines données
            if request.user.role == 'visiteur':
                # Supprimer les informations sensibles
                sensitive_fields = [
                    'last_name', 'place_of_birth', 'arrival_reason', 'arrival_circumstances',
                    'family_background', 'emergency_contact_name', 'emergency_contact_phone',
                    'emergency_contact_relation', 'medical_conditions', 'allergies',
                    'medications', 'birth_certificate', 'medical_records'
                ]
                for field in sensitive_fields:
                    data.pop(field, None)
                
                # Anonymiser le nom de famille
                data['last_name'] = '***'
            
            # Vérifier les permissions pour les dossiers confidentiels
            if instance.is_confidential and not instance.can_be_viewed_by(request.user):
                return {'error': _('Accès non autorisé à ce dossier confidentiel.')}
        
        return data

class ChildCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'enfants"""
    
    class Meta:
        model = Child
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'arrival_date', 'arrival_reason', 'status', 'case_worker',
            'medical_conditions', 'allergies', 'photo'
        ]
    
    def create(self, validated_data):
        """Création d'un enfant avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ChildPublicSerializer(serializers.ModelSerializer):
    """Serializer pour l'affichage public des enfants (anonymisé)"""
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Child
        fields = ['id', 'first_name', 'age', 'gender', 'status', 'photo', 'arrival_date']

class ChildNoteSerializer(serializers.ModelSerializer):
    """Serializer pour les notes sur les enfants"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = ChildNote
        fields = '__all__'
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """Création d'une note avec l'auteur"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class ChildDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents des enfants"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = ChildDocument
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_by', 'uploaded_at')
    
    def get_file_size(self, obj):
        """Retourne la taille du fichier en format lisible"""
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return None
    
    def create(self, validated_data):
        """Création d'un document avec l'utilisateur qui l'a téléchargé"""
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer pour les dossiers médicaux"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    child_name = serializers.CharField(source='child.full_name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def validate_visit_date(self, value):
        """Validation de la date de visite"""
        from datetime import datetime
        if value > datetime.now():
            raise serializers.ValidationError(_("La date de visite ne peut pas être dans le futur."))
        return value
    
    def validate_follow_up_date(self, value):
        """Validation de la date de suivi"""
        if value:
            from datetime import date
            if value < date.today():
                raise serializers.ValidationError(_("La date de suivi ne peut pas être dans le passé."))
        return value
    
    def create(self, validated_data):
        """Création d'un dossier médical avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ChildStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des enfants"""
    total_children = serializers.IntegerField()
    children_by_status = serializers.DictField()
    children_by_age_group = serializers.DictField()
    children_by_gender = serializers.DictField()
    recent_arrivals = serializers.IntegerField()
    children_needing_medical_attention = serializers.IntegerField()
