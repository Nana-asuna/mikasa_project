from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Report, ReportTemplate, Dashboard

class ReportSerializer(serializers.ModelSerializer):
    """Serializer pour les rapports"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'file', 'file_size', 'status')
    
    def get_file_size_mb(self, obj):
        """Retourne la taille du fichier en MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les modèles de rapports"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        """Création avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class DashboardSerializer(serializers.ModelSerializer):
    """Serializer pour les tableaux de bord"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """Création avec le propriétaire"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
