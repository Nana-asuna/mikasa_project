from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.db import transaction
import logging
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def get_client_ip(request) -> str:
    """Obtient l'adresse IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip

def get_user_agent(request) -> str:
    """Obtient le User-Agent du client"""
    return request.META.get('HTTP_USER_AGENT', '')

def generate_secure_token(length: int = 32) -> str:
    """Génère un token sécurisé"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_sensitive_data(data: str) -> str:
    """Hash des données sensibles"""
    return hashlib.sha256(data.encode()).hexdigest()

def send_notification_email(
    recipient_email: str,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    from_email: Optional[str] = None
) -> bool:
    """Envoie un email de notification"""
    try:
        html_message = render_to_string(template_name, context)
        
        send_mail(
            subject=subject,
            message='',  # Version texte vide, on utilise HTML
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Email envoyé avec succès à {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi d'email à {recipient_email}: {str(e)}")
        return False

def cache_key_for_user(user_id: str, key_suffix: str) -> str:
    """Génère une clé de cache pour un utilisateur"""
    return f"user_{user_id}_{key_suffix}"

def invalidate_user_cache(user_id: str, patterns: list = None) -> None:  # type: ignore[attr-defined]
    """Invalide le cache d'un utilisateur"""
    if patterns is None:
        patterns = ['profile', 'permissions', 'notifications']
    
    for pattern in patterns:
        cache_key = cache_key_for_user(user_id, pattern)
        cache.delete(cache_key)

def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier"""
    import re
    # Supprimer les caractères dangereux
    filename = re.sub(r'[^\w\s-.]', '', filename)
    # Remplacer les espaces par des underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename

def validate_file_type(file, allowed_types: list) -> bool:
    """Valide le type d'un fichier"""
    import magic
    
    try:
        file_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Remettre le curseur au début
        return file_type in allowed_types
    except Exception as e:
        logger.error(f"Erreur lors de la validation du type de fichier: {str(e)}")
        return False

def calculate_age(birth_date) -> int:
    """Calcule l'âge à partir d'une date de naissance"""
    from datetime import date
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )

def format_currency(amount, currency='EUR') -> str:
    """Formate un montant en devise"""
    if currency == 'EUR':
        return f"{amount:.2f} €"
    elif currency == 'USD':
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def generate_reference_number(prefix: str, model_instance=None) -> str:
    """Génère un numéro de référence unique"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    if model_instance and hasattr(model_instance, 'id'):
        unique_part = str(model_instance.id)[:8]
    else:
        unique_part = generate_secure_token(8)
    
    return f"{prefix}-{timestamp}-{unique_part}"

def log_user_action(user, action: str, details: Dict[str, Any] = None) -> None:  # type: ignore[attr-defined]
    """Enregistre une action utilisateur"""
    log_data = {
        'user_id': user.id,
        'user_email': user.email,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    
    logger.info(f"User action: {log_data}")

def check_password_strength(password: str) -> Dict[str, Any]:
    """Vérifie la force d'un mot de passe"""
    import re
    
    checks = {
        'length': len(password) >= 12,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'digit': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
    }
    
    score = sum(checks.values())
    
    if score == 5:
        strength = 'very_strong'
    elif score >= 4:
        strength = 'strong'
    elif score >= 3:
        strength = 'medium'
    elif score >= 2:
        strength = 'weak'
    else:
        strength = 'very_weak'
    
    return {
        'strength': strength,
        'score': score,
        'checks': checks,
        'suggestions': get_password_suggestions(checks)
    }

def get_password_suggestions(checks: Dict[str, bool]) -> list:
    """Retourne des suggestions pour améliorer le mot de passe"""
    suggestions = []
    
    if not checks['length']:
        suggestions.append(_("Utilisez au moins 12 caractères"))
    if not checks['uppercase']:
        suggestions.append(_("Ajoutez au moins une lettre majuscule"))
    if not checks['lowercase']:
        suggestions.append(_("Ajoutez au moins une lettre minuscule"))
    if not checks['digit']:
        suggestions.append(_("Ajoutez au moins un chiffre"))
    if not checks['special']:
        suggestions.append(_("Ajoutez au moins un caractère spécial"))
    
    return suggestions

@transaction.atomic
def bulk_create_with_history(model_class, objects: list, batch_size: int = 1000):
    """Création en lot avec historique"""
    created_objects = []
    
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        created_batch = model_class.objects.bulk_create(batch)
        created_objects.extend(created_batch)
        
        logger.info(f"Créé {len(created_batch)} objets {model_class.__name__}")
    
    return created_objects

def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
    """Chiffre des données sensibles"""
    from cryptography.fernet import Fernet
    
    if key is None:
        key = settings.SECRET_KEY[:32].ljust(32, '0').encode()
    
    f = Fernet(Fernet.generate_key())
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Déchiffre des données sensibles"""
    from cryptography.fernet import Fernet
    key_bytes = None  # type: ignore[assignment]
    if key is None:
        key_bytes = settings.SECRET_KEY[:32].ljust(32, '0').encode()
    else:
        key_bytes = key if isinstance(key, bytes) else key.encode()
    f = Fernet(key_bytes)  # type: ignore[arg-type]
    decrypted_data = f.decrypt(encrypted_data.encode())
    return decrypted_data.decode()

def create_audit_trail(user, action: str, model_instance, changes: Dict[str, Any] = None):  # type: ignore[attr-defined]
    """Crée une piste d'audit"""
    from apps.core.models import AuditTrail
    
    AuditTrail.objects.create(  # type: ignore[attr-defined,call-arg]
        user=user,
        action=action,
        model_name=model_instance.__class__.__name__,
        object_id=str(model_instance.pk),
        changes=changes or {},
        ip_address=getattr(user, '_current_ip', None),
        user_agent=getattr(user, '_current_user_agent', None)
    )

def validate_business_rules(model_instance, rules: Dict[str, callable]) -> Dict[str, list]:  # type: ignore[attr-defined,call-arg]
    """Valide les règles métier"""
    errors = {}  # type: ignore[assignment]
    
    for rule_name, rule_func in rules.items():
        try:
            if not rule_func(model_instance):
                errors[rule_name] = [f"Règle métier '{rule_name}' non respectée"]  # type: ignore[call-arg]
        except Exception as e:
            errors[rule_name] = [f"Erreur lors de la validation de '{rule_name}': {str(e)}"]  # type: ignore[call-arg]
    
    return errors  # type: ignore[return-value]

def generate_qr_code(data: str, size: int = 10) -> bytes:
    """Génère un QR code"""
    import qrcode
    from io import BytesIO
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # type: ignore[attr-defined]
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')  # type: ignore[attr-defined]
    return buffer.getvalue()
