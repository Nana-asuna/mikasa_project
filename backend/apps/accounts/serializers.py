from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription des utilisateurs"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'phone_number')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validation personnalisée de l'email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("Un utilisateur avec cet email existe déjà."))
        
        # Validation du domaine email pour certains rôles
        if '@' in value:
            domain = value.split('@')[1]
            suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            if domain in suspicious_domains:
                raise serializers.ValidationError(_("Ce domaine email n'est pas autorisé."))
        
        return value
    
    def validate_username(self, value):
        """Validation du nom d'utilisateur"""
        if len(value) < 3:
            raise serializers.ValidationError(_("Le nom d'utilisateur doit contenir au moins 3 caractères."))
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(_("Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores."))
        
        return value
    
    def validate_role(self, value):
        """Validation du rôle"""
        # Seuls les admins peuvent créer d'autres admins
        request = self.context.get('request')
        if value == 'admin' and (not request or not request.user.has_role('admin')):
            raise serializers.ValidationError(_("Vous n'avez pas les permissions pour créer un administrateur."))
        
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Les mots de passe ne correspondent pas."))
        
        # Vérification que le mot de passe ne contient pas d'informations personnelles
        password = attrs['password']
        if (attrs['first_name'].lower() in password.lower() or 
            attrs['last_name'].lower() in password.lower() or
            attrs['username'].lower() in password.lower()):
            raise serializers.ValidationError(_("Le mot de passe ne doit pas contenir vos informations personnelles."))
        
        return attrs
    
    def create(self, validated_data):
        """Création de l'utilisateur"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Créer le profil utilisateur
        UserProfile.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validation de la connexion"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                raise serializers.ValidationError(_("Email ou mot de passe incorrect."))
            
            if not user.is_active:
                raise serializers.ValidationError(_("Ce compte est désactivé."))
            
            if not user.is_verified:
                raise serializers.ValidationError(_("Veuillez vérifier votre email avant de vous connecter."))
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(_("Email et mot de passe requis."))

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 
                 'role', 'phone_number', 'is_verified', 'last_login', 'created_at', 'profile')
        read_only_fields = ('id', 'last_login', 'created_at', 'is_verified')

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validation de l'ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("L'ancien mot de passe est incorrect."))
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("Les nouveaux mots de passe ne correspondent pas."))
        
        # Vérifier que le nouveau mot de passe est différent de l'ancien
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(_("Le nouveau mot de passe doit être différent de l'ancien."))
        
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    """Serializer pour la réinitialisation de mot de passe"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validation de l'email"""
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError(_("Ce compte est désactivé."))
        except User.DoesNotExist:
            # Ne pas révéler si l'email existe ou non pour des raisons de sécurité
            pass
        
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour la confirmation de réinitialisation de mot de passe"""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("Les mots de passe ne correspondent pas."))
        
        return attrs
