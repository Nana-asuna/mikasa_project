from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import NotificationTemplate, Notification, NotificationPreference

class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les modèles de notifications"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at')

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer pour les préférences de notifications"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
