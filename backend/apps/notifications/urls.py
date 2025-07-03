from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Notifications
    # path('', views.NotificationListView.as_view(), name='notification-list'),  # type: ignore[attr-defined]
    # path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),  # type: ignore[attr-defined]
    # path('<uuid:pk>/read/', views.mark_as_read, name='mark-as-read'),  # type: ignore[attr-defined]
    # path('mark-all-read/', views.mark_all_as_read, name='mark-all-as-read'),  # type: ignore[attr-defined]
    # path('count/', views.notification_count, name='notification-count'),  # type: ignore[attr-defined]
    
    # Preferences
    # path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),  # type: ignore[attr-defined]
    
    # Templates
    # path('templates/', views.NotificationTemplateListCreateView.as_view(), name='template-list-create'),  # type: ignore[attr-defined]
    
    # Router URLs
    path('', include(router.urls)),
]
