from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()

urlpatterns = [
    # Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Email verification
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    
    # Password management
    path('change-password/', views.change_password, name='change_password'),
    path('reset-password/', views.password_reset_request, name='password_reset'),
    path('reset-password-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Router URLs
    path('', include(router.urls)),
]
