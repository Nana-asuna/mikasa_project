from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.conf import settings
import logging
import time
import json

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware pour ajouter des en-têtes de sécurité"""
    
    def process_response(self, request, response):
        # En-têtes de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS en production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response

class AuditLogMiddleware(MiddlewareMixin):
    """Middleware pour l'audit des actions"""
    
    def process_request(self, request):
        # Enregistrer le début de la requête
        request._audit_start_time = time.time()
        
        # Exclure certaines URLs de l'audit
        excluded_paths = ['/health/', '/metrics/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in excluded_paths):
            return None
        
        # Préparer les données d'audit
        request._audit_data = {
            'method': request.method,
            'path': request.path,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': time.time(),
        }
        
        return None
    
    def process_response(self, request, response):
        # Enregistrer la fin de la requête
        if hasattr(request, '_audit_data'):
            duration = time.time() - request._audit_start_time
            
            audit_data = request._audit_data
            audit_data.update({
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
            })
            
            # Enregistrer les actions sensibles
            if (request.method in ['POST', 'PUT', 'DELETE'] or 
                response.status_code >= 400):
                logger.info(f"Audit: {json.dumps(audit_data, default=str)}")
        
        return response
    
    def get_client_ip(self, request):
        """Obtient l'adresse IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware pour la limitation de débit"""
    
    def process_request(self, request):
        # Exclure certaines URLs
        excluded_paths = ['/health/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in excluded_paths):
            return None
        
        ip_address = self.get_client_ip(request)
        
        # Différentes limites selon l'endpoint
        if request.path.startswith('/api/auth/'):
            limit = 5  # 5 tentatives par minute pour l'auth
            window = 60
        elif request.method == 'POST':
            limit = 30  # 30 POST par minute
            window = 60
        else:
            limit = 100  # 100 requêtes par minute pour le reste
            window = 60
        
        # Clé de cache
        cache_key = f"rate_limit_{ip_address}_{request.path}"
        
        # Vérifier la limite
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit:
            logger.warning(f"Rate limit exceeded for IP {ip_address} on {request.path}")
            return JsonResponse({
                'error': _('Trop de requêtes. Veuillez réessayer plus tard.'),
                'retry_after': window
            }, status=429)
        
        # Incrémenter le compteur
        cache.set(cache_key, current_requests + 1, window)
        
        return None
    
    def get_client_ip(self, request):
        """Obtient l'adresse IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class APIVersionMiddleware(MiddlewareMixin):
    """Middleware pour la gestion des versions d'API"""
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            # Récupérer la version depuis l'en-tête ou l'URL
            version = request.META.get('HTTP_API_VERSION', 'v1')
            
            # Valider la version
            supported_versions = ['v1', 'v2']
            if version not in supported_versions:
                return JsonResponse({
                    'error': _('Version d\'API non supportée'),
                    'supported_versions': supported_versions
                }, status=400)
            
            request.api_version = version
        
        return None

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware pour logger les requêtes"""
    
    def process_request(self, request):
        # Logger les requêtes sensibles
        if request.method in ['POST', 'PUT', 'DELETE']:
            logger.info(f"Request: {request.method} {request.path} from {self.get_client_ip(request)}")
        
        return None
    
    def process_exception(self, request, exception):
        # Logger les exceptions
        logger.error(f"Exception in {request.method} {request.path}: {str(exception)}")
        return None
    
    def get_client_ip(self, request):
        """Obtient l'adresse IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class DatabaseConnectionMiddleware(MiddlewareMixin):
    """Middleware pour optimiser les connexions à la base de données"""
    
    def process_request(self, request):
        from django.db import connection
        
        # Réinitialiser les requêtes pour le debug
        if settings.DEBUG:
            connection.queries_log.clear()
        
        return None
    
    def process_response(self, request, response):
        from django.db import connection
        
        # Logger les requêtes lentes en debug
        if settings.DEBUG:
            slow_queries = [q for q in connection.queries if float(q['time']) > 0.1]
            if slow_queries:
                logger.warning(f"Slow queries detected: {len(slow_queries)} queries > 100ms")
        
        return response

class CORSMiddleware(MiddlewareMixin):
    """Middleware CORS personnalisé pour plus de contrôle"""
    
    def process_response(self, request, response):
        # Ajouter les en-têtes CORS seulement pour les API
        if request.path.startswith('/api/'):
            origin = request.META.get('HTTP_ORIGIN')
            
            # Vérifier si l'origine est autorisée
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            
            if origin in allowed_origins or settings.DEBUG:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Accept, Content-Type, Authorization, X-Requested-With'
                response['Access-Control-Max-Age'] = '3600'
        
        return response
