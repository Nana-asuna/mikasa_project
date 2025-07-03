from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import SecurityIncident, AuditTrail
import logging
import json
import hashlib
import time
from datetime import datetime, timedelta

logger = logging.getLogger('django.security')

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware pour ajouter des en-têtes de sécurité avancés"""
    
    def process_response(self, request, response):
        # En-têtes de sécurité de base
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (anciennement Feature Policy)
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # Content Security Policy
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_parts = []
            csp_parts.append(f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}")
            csp_parts.append(f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}")
            csp_parts.append(f"style-src {' '.join(settings.CSP_STYLE_SRC)}")
            csp_parts.append(f"img-src {' '.join(settings.CSP_IMG_SRC)}")
            csp_parts.append(f"font-src {' '.join(settings.CSP_FONT_SRC)}")
            csp_parts.append(f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}")
            csp_parts.append(f"frame-ancestors {' '.join(settings.CSP_FRAME_ANCESTORS)}")
            
            response['Content-Security-Policy'] = '; '.join(csp_parts)
        
        # HSTS en production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        # En-tête personnalisé pour identifier l'application
        response['X-Powered-By'] = 'Orphanage Management System'
        
        return response

class ThreatDetectionMiddleware(MiddlewareMixin):
    """Middleware pour détecter les menaces de sécurité"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'union\s+select',  # SQL Injection
            r'drop\s+table',  # SQL Injection
            r'exec\s*\(',  # Code injection
            r'eval\s*\(',  # Code injection
            r'\.\./',  # Path traversal
            r'<iframe[^>]*>',  # Iframe injection
        ]
    
    def process_request(self, request):
        # Vérifier les patterns suspects dans les données
        suspicious_data = self._check_for_threats(request)
        
        if suspicious_data:
            # Logger l'incident
            logger.warning(f"Threat detected from {self._get_client_ip(request)}: {suspicious_data}")
            
            # Créer un incident de sécurité
            SecurityIncident.objects.create(
                title="Tentative d'attaque détectée",
                description=f"Pattern suspect détecté: {suspicious_data}",
                severity='high',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_data={
                    'path': request.path,
                    'method': request.method,
                    'data': str(suspicious_data)[:500]  # Limiter la taille
                },
                affected_user=request.user if request.user.is_authenticated else None
            )
            
            # Bloquer la requête
            return JsonResponse({
                'error': _('Requête suspecte détectée et bloquée.'),
                'code': 'THREAT_DETECTED'
            }, status=403)
        
        return None
    
    def _check_for_threats(self, request):
        """Vérifie la présence de patterns suspects"""
        import re
        
        # Données à vérifier
        data_to_check = []
        
        # Paramètres GET
        for key, value in request.GET.items():
            data_to_check.append(f"{key}={value}")
        
        # Données POST
        if hasattr(request, 'body') and request.body:
            try:
                if request.content_type == 'application/json':
                    data_to_check.append(request.body.decode('utf-8'))
                elif request.content_type == 'application/x-www-form-urlencoded':
                    for key, value in request.POST.items():
                        data_to_check.append(f"{key}={value}")
            except:
                pass
        
        # Vérifier chaque pattern
        for data in data_to_check:
            for pattern in self.suspicious_patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    return data[:100]  # Retourner les premiers 100 caractères
        
        return None
    
    def _get_client_ip(self, request):
        """Obtient l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware avancé pour la limitation de débit"""
    
    def process_request(self, request):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return None
        
        ip_address = self._get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Déterminer la limite selon l'endpoint
        rate_limit = self._get_rate_limit(request)
        
        if not rate_limit:
            return None
        
        # Clés de cache
        ip_key = f"rate_limit_ip_{ip_address}_{request.path}"
        user_key = f"rate_limit_user_{user_id}_{request.path}" if user_id else None
        
        # Vérifier les limites
        if self._is_rate_limited(ip_key, rate_limit):
            logger.warning(f"Rate limit exceeded for IP {ip_address}")
            return self._rate_limit_response(rate_limit)
        
        if user_key and self._is_rate_limited(user_key, rate_limit):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return self._rate_limit_response(rate_limit)
        
        return None
    
    def _get_rate_limit(self, request):
        """Détermine la limite de débit pour la requête"""
        path = request.path
        method = request.method
        
        # Limites spécifiques par endpoint
        if '/api/v1/auth/login/' in path:
            return {'limit': 5, 'window': 300}  # 5 tentatives par 5 minutes
        elif '/api/v1/auth/register/' in path:
            return {'limit': 3, 'window': 3600}  # 3 inscriptions par heure
        elif '/api/v1/auth/password-reset/' in path:
            return {'limit': 3, 'window': 3600}  # 3 reset par heure
        elif method == 'POST' and '/api/' in path:
            return {'limit': 30, 'window': 3600}  # 30 POST par heure
        elif '/api/' in path:
            return {'limit': 100, 'window': 3600}  # 100 requêtes par heure
        
        return None
    
    def _is_rate_limited(self, cache_key, rate_limit):
        """Vérifie si la limite est atteinte"""
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= rate_limit['limit']:
            return True
        
        # Incrémenter le compteur
        cache.set(cache_key, current_requests + 1, rate_limit['window'])
        return False
    
    def _rate_limit_response(self, rate_limit):
        """Retourne une réponse de limitation de débit"""
        return JsonResponse({
            'error': _('Trop de requêtes. Veuillez réessayer plus tard.'),
            'retry_after': rate_limit['window'],
            'code': 'RATE_LIMITED'
        }, status=429)
    
    def _get_client_ip(self, request):
        """Obtient l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class AuditMiddleware(MiddlewareMixin):
    """Middleware pour l'audit automatique des actions"""
    
    def process_request(self, request):
        # Marquer le début de la requête
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Exclure certaines URLs de l'audit
        excluded_paths = ['/health/', '/metrics/', '/static/', '/media/', '/admin/jsi18n/']
        if any(request.path.startswith(path) for path in excluded_paths):
            return response
        
        # Calculer la durée
        duration = time.time() - getattr(request, '_audit_start_time', time.time())
        
        # Auditer les actions sensibles
        if (request.method in ['POST', 'PUT', 'DELETE', 'PATCH'] or 
            response.status_code >= 400 or
            '/api/' in request.path):
            
            self._create_audit_log(request, response, duration)
        
        return response
    
    def _create_audit_log(self, request, response, duration):
        """Crée un log d'audit"""
        try:
            # Déterminer l'action
            action = self._determine_action(request.method, request.path)
            
            # Données de la requête (limitées pour la sécurité)
            request_data = {}
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.content_type == 'application/json':
                    try:
                        request_data = json.loads(request.body.decode('utf-8'))
                        # Supprimer les données sensibles
                        sensitive_fields = ['password', 'token', 'secret', 'key']
                        for field in sensitive_fields:
                            if field in request_data:
                                request_data[field] = '[REDACTED]'
                    except:
                        pass
            
            AuditTrail.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if hasattr(request, 'session') else '',
                action=action,
                model_name=self._extract_model_name(request.path),
                object_id=self._extract_object_id(request.path),
                changes=request_data,
                additional_data={
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'response_size': len(response.content) if hasattr(response, 'content') else 0,
                },
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_path=request.path,
                request_method=request.method,
            )
        except Exception as e:
            logger.error(f"Erreur lors de la création du log d'audit: {str(e)}")
    
    def _determine_action(self, method, path):
        """Détermine l'action basée sur la méthode HTTP"""
        if method == 'POST':
            return 'create'
        elif method == 'GET':
            return 'read'
        elif method in ['PUT', 'PATCH']:
            return 'update'
        elif method == 'DELETE':
            return 'delete'
        else:
            return 'unknown'
    
    def _extract_model_name(self, path):
        """Extrait le nom du modèle depuis le chemin"""
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'v1':
            return parts[2]
        return 'unknown'
    
    def _extract_object_id(self, path):
        """Extrait l'ID de l'objet depuis le chemin"""
        parts = path.strip('/').split('/')
        # Chercher un UUID ou un ID numérique
        for part in parts:
            if (len(part) == 36 and part.count('-') == 4) or part.isdigit():
                return part
        return ''
    
    def _get_client_ip(self, request):
        """Obtient l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
