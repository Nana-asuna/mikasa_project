from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class HasRolePermission(permissions.BasePermission):
    """Permission basée sur le rôle de l'utilisateur"""
    
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.role in self.allowed_roles or request.user.role == 'admin'

class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission pour le propriétaire ou l'admin"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin a tous les droits
        if request.user.role == 'admin':
            return True
        
        # Vérifier si l'utilisateur est le propriétaire
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False

class CanManageChildren(permissions.BasePermission):
    """Permission pour gérer les enfants"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        allowed_roles = ['admin', 'assistant_social', 'soignant']
        return request.user.role in allowed_roles

class CanManageInventory(permissions.BasePermission):
    """Permission pour gérer l'inventaire"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        allowed_roles = ['admin', 'logisticien']
        return request.user.role in allowed_roles

class CanViewFinancialData(permissions.BasePermission):
    """Permission pour voir les données financières"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        allowed_roles = ['admin']
        return request.user.role in allowed_roles or request.user.has_perm('donations.can_view_financial_info')

class CanManageFamilies(permissions.BasePermission):
    """Permission pour gérer les familles"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        allowed_roles = ['admin', 'assistant_social']
        return request.user.role in allowed_roles

class CanGenerateReports(permissions.BasePermission):
    """Permission pour générer des rapports"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        allowed_roles = ['admin', 'assistant_social']
        return request.user.role in allowed_roles or request.user.has_perm('reports.can_generate_reports')

class CanViewConfidentialData(permissions.BasePermission):
    """Permission pour voir les données confidentielles"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (request.user.role in ['admin', 'assistant_social'] or 
                request.user.has_perm('children.view_confidential_child'))

class RoleBasedPermission(permissions.BasePermission):
    """Permission dynamique basée sur les rôles"""
    
    def __init__(self, role_permissions):
        """
        role_permissions: dict avec les permissions par rôle
        Exemple: {
            'admin': ['GET', 'POST', 'PUT', 'DELETE'],
            'soignant': ['GET', 'POST'],
            'visiteur': ['GET']
        }
        """
        self.role_permissions = role_permissions
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = request.user.role
        allowed_methods = self.role_permissions.get(user_role, [])
        
        # Admin a tous les droits
        if user_role == 'admin':
            return True
        
        return request.method in allowed_methods
