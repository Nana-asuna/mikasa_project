from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Family, FamilyMember, Placement, FamilyVisit

class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer pour les membres de famille"""
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = FamilyMember
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class FamilySerializer(serializers.ModelSerializer):
    """Serializer pour les familles"""
    members = FamilyMemberSerializer(many=True, read_only=True)
    primary_contact_full_name = serializers.ReadOnlyField()
    secondary_contact_full_name = serializers.ReadOnlyField()
    current_children_count = serializers.ReadOnlyField()
    available_capacity = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    case_worker_name = serializers.CharField(source='case_worker.get_full_name', read_only=True)
    
    class Meta:
        model = Family
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs.get('preferred_age_max') and attrs.get('preferred_age_min'):
            if attrs['preferred_age_max'] < attrs['preferred_age_min']:
                raise serializers.ValidationError(_("L'âge maximum doit être supérieur à l'âge minimum."))
        
        return attrs
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class PlacementSerializer(serializers.ModelSerializer):
    """Serializer pour les placements"""
    child_name = serializers.CharField(source='child.full_name', read_only=True)
    family_name = serializers.CharField(source='family.family_name', read_only=True)
    case_worker_name = serializers.CharField(source='case_worker.get_full_name', read_only=True)
    duration_days = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Placement
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs.get('actual_end_date') and attrs['actual_end_date'] < attrs['start_date']:
            raise serializers.ValidationError(_("La date de fin ne peut pas être antérieure à la date de début."))
        
        return attrs
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class FamilyVisitSerializer(serializers.ModelSerializer):
    """Serializer pour les visites de familles"""
    family_name = serializers.CharField(source='family.family_name', read_only=True)
    visitor_name = serializers.CharField(source='visitor.get_full_name', read_only=True)
    
    class Meta:
        model = FamilyVisit
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_scheduled_date(self, value):
        """Validation de la date de visite"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError(_("La date de visite ne peut pas être dans le passé."))
        return value
