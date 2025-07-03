from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

@require_http_methods(["GET"])
def system_status(request):
    """System status with database and cache check"""
    status = {
        'database': 'unknown',
        'cache': 'unknown',
        'timestamp': timezone.now().isoformat()
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'healthy'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check cache
    try:
        cache.set('health_check', 'test', 10)
        if cache.get('health_check') == 'test':
            status['cache'] = 'healthy'
        else:
            status['cache'] = 'error: cache not working'
    except Exception as e:
        status['cache'] = f'error: {str(e)}'
        logger.error(f"Cache health check failed: {str(e)}")
    
    return JsonResponse(status)

# Error handlers
def bad_request(request, exception):
    return JsonResponse({
        'error': 'Bad Request',
        'message': 'La requête est malformée.'
    }, status=400)

def permission_denied(request, exception):
    return JsonResponse({
        'error': 'Permission Denied',
        'message': 'Vous n\'avez pas les permissions nécessaires.'
    }, status=403)

def not_found(request, exception):
    return JsonResponse({
        'error': 'Not Found',
        'message': 'La ressource demandée n\'existe pas.'
    }, status=404)

def server_error(request):
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'Une erreur interne s\'est produite.'
    }, status=500)
