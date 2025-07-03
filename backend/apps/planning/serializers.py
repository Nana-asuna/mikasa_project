from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Event, Schedule, Availability, Task, Shift, ShiftAssignment

class EventSerializer(serializers.ModelSerializer):
    """Serializer pour les événements"""
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    children_names = serializers.StringRelatedField(source='children', many=True, read_only=True)
    staff_names = serializers.StringRelatedField(source='staff_members', many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['end_datetime'] <= attrs['start_datetime']:
            raise serializers.ValidationError(_("La date de fin doit être postérieure à la date de début."))
        
        if attrs['recurrence_type'] != 'none' and not attrs.get('recurrence_end_date'):
            raise serializers.ValidationError(_("Une date de fin de récurrence est requise."))
        
        return attrs
    
    def create(self, validated_data):
        """Création avec l'organisateur"""
        validated_data['organizer'] = self.context['request'].user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer pour les plannings"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    working_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class AvailabilitySerializer(serializers.ModelSerializer):
    """Serializer pour les disponibilités"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Availability
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['end_datetime'] <= attrs['start_datetime']:
            raise serializers.ValidationError(_("La date de fin doit être postérieure à la date de début."))
        return attrs

class TaskSerializer(serializers.ModelSerializer):
    """Serializer pour les tâches"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    related_child_name = serializers.CharField(source='related_child.full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        """Création avec le créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ShiftAssignmentSerializer(serializers.ModelSerializer):
    """Serializer pour les attributions d'équipes"""
    staff_member_name = serializers.CharField(source='staff_member.get_full_name', read_only=True)
    
    class Meta:
        model = ShiftAssignment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class ShiftSerializer(serializers.ModelSerializer):
    """Serializer pour les équipes"""
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assignments = ShiftAssignmentSerializer(source='shiftassignment_set', many=True, read_only=True)
    current_staff_count = serializers.ReadOnlyField()
    is_fully_staffed = serializers.ReadOnlyField()
    
    class Meta:
        model = Shift
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        """Création avec le créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
