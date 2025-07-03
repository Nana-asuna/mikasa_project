from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re
import string

class CustomPasswordValidator:
    """Validateur de mot de passe personnalisé avec règles strictes"""
    
    def __init__(self, min_uppercase=1, min_lowercase=1, min_digits=1, 
                 min_special=1, forbidden_patterns=None):
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special
        self.forbidden_patterns = forbidden_patterns or []
    
    def validate(self, password, user=None):
        """Valide le mot de passe selon les règles définies"""
        errors = []
        
        # Vérifier les majuscules
        uppercase_count = sum(1 for c in password if c.isupper())
        if uppercase_count < self.min_uppercase:
            errors.append(
                _('Le mot de passe doit contenir au moins %(min)d majuscule(s).') % 
                {'min': self.min_uppercase}
            )
        
        # Vérifier les minuscules
        lowercase_count = sum(1 for c in password if c.islower())
        if lowercase_count < self.min_lowercase:
            errors.append(
                _('Le mot de passe doit contenir au moins %(min)d minuscule(s).') % 
                {'min': self.min_lowercase}
            )
        
        # Vérifier les chiffres
        digit_count = sum(1 for c in password if c.isdigit())
        if digit_count < self.min_digits:
            errors.append(
                _('Le mot de passe doit contenir au moins %(min)d chiffre(s).') % 
                {'min': self.min_digits}
            )
        
        # Vérifier les caractères spéciaux
        special_chars = set(string.punctuation)
        special_count = sum(1 for c in password if c in special_chars)
        if special_count < self.min_special:
            errors.append(
                _('Le mot de passe doit contenir au moins %(min)d caractère(s) spécial(aux).') % 
                {'min': self.min_special}
            )
        
        # Vérifier les motifs interdits
        for pattern in self.forbidden_patterns:
            if pattern.lower() in password.lower():
                errors.append(
                    _('Le mot de passe ne doit pas contenir "%(pattern)s".') % 
                    {'pattern': pattern}
                )
        
        # Vérifier les séquences communes
        if self._has_common_sequences(password):
            errors.append(
                _('Le mot de passe ne doit pas contenir de séquences communes (123, abc, etc.).')
            )
        
        # Vérifier les informations personnelles si utilisateur fourni
        if user:
            if self._contains_personal_info(password, user):
                errors.append(
                    _('Le mot de passe ne doit pas contenir vos informations personnelles.')
                )
        
        if errors:
            raise ValidationError(errors)
    
    def _has_common_sequences(self, password):
        """Vérifie la présence de séquences communes"""
        password_lower = password.lower()
        
        # Séquences numériques
        for i in range(len(password_lower) - 2):
            if password_lower[i:i+3].isdigit():
                nums = [int(c) for c in password_lower[i:i+3]]
                if nums[1] == nums[0] + 1 and nums[2] == nums[1] + 1:
                    return True
        
        # Séquences alphabétiques
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        for i in range(len(alphabet) - 2):
            if alphabet[i:i+3] in password_lower:
                return True
        
        # Séquences de clavier
        keyboard_sequences = ['qwerty', 'azerty', 'qwertz', 'asdf', 'zxcv']
        for seq in keyboard_sequences:
            if seq in password_lower:
                return True
        
        return False
    
    def _contains_personal_info(self, password, user):
        """Vérifie si le mot de passe contient des informations personnelles"""
        password_lower = password.lower()
        
        # Informations à vérifier
        personal_info = [
            user.username.lower() if user.username else '',
            user.first_name.lower() if user.first_name else '',
            user.last_name.lower() if user.last_name else '',
            user.email.split('@')[0].lower() if user.email else '',
        ]
        
        for info in personal_info:
            if info and len(info) > 2 and info in password_lower:
                return True
        
        return False
    
    def get_help_text(self):
        """Retourne le texte d'aide pour le validateur"""
        return _(
            'Votre mot de passe doit contenir au moins %(uppercase)d majuscule(s), '
            '%(lowercase)d minuscule(s), %(digits)d chiffre(s) et %(special)d '
            'caractère(s) spécial(aux). Il ne doit pas contenir de séquences '
            'communes ou vos informations personnelles.'
        ) % {
            'uppercase': self.min_uppercase,
            'lowercase': self.min_lowercase,
            'digits': self.min_digits,
            'special': self.min_special,
        }
