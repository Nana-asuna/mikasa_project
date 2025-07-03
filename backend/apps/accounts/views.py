from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging
from django.utils import timezone

from .models import User, LoginAttempt
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
)
from apps.core.permissions import IsOwnerOrAdmin
from apps.core.utils import get_client_ip, get_user_agent

logger = logging.getLogger(__name__)

class LoginRateThrottle(UserRateThrottle):
    scope = 'login'

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='post')
class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour l'obtention de tokens JWT avec sécurité renforcée"""
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request, *args, **kwargs):
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        email = request.data.get('email', '')  # type: ignore[attr-defined]
        
        # Vérifier si l'IP est bloquée
        blocked_key = f"blocked_ip_{ip_address}"
        if cache.get(blocked_key):
            logger.warning(f"Tentative de connexion depuis une IP bloquée: {ip_address}")
            return Response(
                {'error': _('Trop de tentatives échouées. Réessayez plus tard.')},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Connexion réussie
                try:
                    user = User.objects.get(email=email)
                    user.failed_login_attempts = 0
                    user.last_ip_address = ip_address
                    user.user_agent = user_agent
                    user.save(update_fields=['failed_login_attempts', 'last_ip_address', 'user_agent'])
                    
                    # Enregistrer la tentative réussie
                    LoginAttempt.objects.create(  # type: ignore[attr-defined]
                        user=user,
                        email=email,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        success=True
                    )
                    
                    logger.info(f"Connexion réussie pour {email} depuis {ip_address}")
                    
                except User.DoesNotExist:  # type: ignore[attr-defined]
                    pass
            else:
                # Connexion échouée
                self._handle_failed_login(email, ip_address, user_agent)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            self._handle_failed_login(email, ip_address, user_agent)
            return Response(
                {'error': _('Erreur interne du serveur.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_failed_login(self, email, ip_address, user_agent):
        """Gère les tentatives de connexion échouées"""
        try:
            user = User.objects.get(email=email)
            user.failed_login_attempts += 1
            user.last_failed_login = timezone.now()
            user.save(update_fields=['failed_login_attempts', 'last_failed_login'])
            
            # Bloquer le compte après 5 tentatives
            if user.failed_login_attempts >= 5:
                user.is_active = False
                user.save(update_fields=['is_active'])
                logger.warning(f"Compte bloqué pour {email} après 5 tentatives échouées")
        except User.DoesNotExist:  # type: ignore[attr-defined]
            pass
        
        # Enregistrer la tentative échouée
        LoginAttempt.objects.create(  # type: ignore[attr-defined]
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason='Invalid credentials'
        )
        
        # Bloquer l'IP après 10 tentatives échouées
        failed_attempts_key = f"failed_attempts_{ip_address}"
        failed_attempts = cache.get(failed_attempts_key, 0) + 1
        cache.set(failed_attempts_key, failed_attempts, 3600)  # 1 heure
        
        if failed_attempts >= 10:
            cache.set(f"blocked_ip_{ip_address}", True, 3600)  # Bloquer pour 1 heure
            logger.warning(f"IP bloquée pour tentatives multiples: {ip_address}")

@method_decorator(ratelimit(key='ip', rate='3/m', method='POST'), name='post')
class UserRegistrationView(generics.CreateAPIView):
    """Vue pour l'inscription des utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Envoyer un email de vérification
        self._send_verification_email(user, request)
        
        logger.info(f"Nouvel utilisateur créé: {user.email}")
        
        return Response({
            'message': _('Compte créé avec succès. Vérifiez votre email pour activer votre compte.'),
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    
    def _send_verification_email(self, user, request):
        """Envoie un email de vérification"""
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
            
            context = {
                'user': user,
                'verification_url': verification_url,
                'site_name': 'Orphanage Management'
            }
            
            subject = _('Vérifiez votre adresse email')
            message = render_to_string('emails/email_verification.html', context)
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de vérification: {str(e)}")

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([AnonRateThrottle])
def verify_email(request, uidb64, token):
    """Vérifie l'adresse email de l'utilisateur"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            
            logger.info(f"Email vérifié pour l'utilisateur: {user.email}")
            
            return Response({
                'message': _('Email vérifié avec succès. Vous pouvez maintenant vous connecter.')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': _('Token de vérification invalide.')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):  # type: ignore[attr-defined]
        return Response({
            'error': _('Lien de vérification invalide.')
        }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Vue pour consulter et modifier le profil utilisateur"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change le mot de passe de l'utilisateur"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']  # type: ignore[index]
        
        # Vérifier l'historique des mots de passe
        from .models import PasswordHistory
        from django.contrib.auth.hashers import check_password
        
        recent_passwords = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:5]  # type: ignore[attr-defined]
        for pwd_history in recent_passwords:
            if check_password(new_password, pwd_history.password_hash):
                return Response({
                    'error': _('Vous ne pouvez pas réutiliser un de vos 5 derniers mots de passe.')
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Sauvegarder l'ancien mot de passe dans l'historique
        PasswordHistory.objects.create(  # type: ignore[attr-defined]
            user=user,
            password_hash=user.password
        )
        
        # Changer le mot de passe
        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.must_change_password = False
        user.save(update_fields=['password', 'password_changed_at', 'must_change_password'])
        
        logger.info(f"Mot de passe changé pour l'utilisateur: {user.email}")
        
        return Response({
            'message': _('Mot de passe changé avec succès.')
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([AnonRateThrottle])
def password_reset_request(request):
    """Demande de réinitialisation de mot de passe"""
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']  # type: ignore[index]
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Générer le token de réinitialisation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Envoyer l'email
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'Orphanage Management'
            }
            
            subject = _('Réinitialisation de votre mot de passe')
            message = render_to_string('emails/password_reset.html', context)
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False
            )
            
            logger.info(f"Email de réinitialisation envoyé à: {email}")
            
        except User.DoesNotExist:  # type: ignore[attr-defined]
            # Ne pas révéler si l'email existe ou non
            pass
        
        return Response({
            'message': _('Si cet email existe, vous recevrez un lien de réinitialisation.')
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request, uidb64, token):
    """Confirme la réinitialisation de mot de passe"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            serializer = PasswordResetConfirmSerializer(data=request.data)
            
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']  # type: ignore[index]
                
                user.set_password(new_password)
                user.password_changed_at = timezone.now()
                user.failed_login_attempts = 0
                user.is_active = True  # Réactiver le compte si bloqué
                user.save(update_fields=['password', 'password_changed_at', 'failed_login_attempts', 'is_active'])
                
                logger.info(f"Mot de passe réinitialisé pour: {user.email}")
                
                return Response({
                    'message': _('Mot de passe réinitialisé avec succès.')
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': _('Token de réinitialisation invalide.')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):  # type: ignore[attr-defined]
        return Response({
            'error': _('Lien de réinitialisation invalide.')
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Déconnexion de l'utilisateur"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        
        logger.info(f"Déconnexion de l'utilisateur: {request.user.email}")
        
        return Response({
            'message': _('Déconnexion réussie.')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        return Response({
            'error': _('Erreur lors de la déconnexion.')
        }, status=status.HTTP_400_BAD_REQUEST)
