from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import Donor, Donation, DonationCampaign, RecurringDonation

class DonorSerializer(serializers.ModelSerializer):
    """Serializer pour les donateurs"""
    total_donations = serializers.ReadOnlyField()
    donation_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Donor
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_email(self, value):
        """Validation de l'email"""
        if Donor.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(_("Un donateur avec cet email existe déjà."))
        return value

class DonationSerializer(serializers.ModelSerializer):
    """Serializer pour les dons"""
    donor_name = serializers.CharField(source='donor.name', read_only=True)
    child_name = serializers.CharField(source='child.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'reference_number')
    
    def validate_amount(self, value):
        """Validation du montant"""
        if value <= 0:
            raise serializers.ValidationError(_("Le montant doit être positif."))
        if value > Decimal('1000000'):
            raise serializers.ValidationError(_("Le montant ne peut pas dépasser 1 000 000."))
        return value
    
    def create(self, validated_data):
        """Création d'un don avec l'utilisateur créateur"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class DonationCampaignSerializer(serializers.ModelSerializer):
    """Serializer pour les campagnes de dons"""
    progress_percentage = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DonationCampaign
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'current_amount')
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['end_date'] <= attrs['start_date']:
            raise serializers.ValidationError(_("La date de fin doit être postérieure à la date de début."))
        return attrs

class RecurringDonationSerializer(serializers.ModelSerializer):
    """Serializer pour les dons récurrents"""
    donor_name = serializers.CharField(source='donor.name', read_only=True)
    
    class Meta:
        model = RecurringDonation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs.get('end_date') and attrs['end_date'] <= attrs['start_date']:
            raise serializers.ValidationError(_("La date de fin doit être postérieure à la date de début."))
        return attrs
