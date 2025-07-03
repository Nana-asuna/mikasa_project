from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Reports
    # path('', views.ReportListCreateView.as_view(), name='report-list-create'),  # type: ignore[attr-defined]
    # path('<uuid:pk>/', views.ReportDetailView.as_view(), name='report-detail'),  # type: ignore[attr-defined]
    # path('<uuid:pk>/download/', views.download_report, name='download-report'),  # type: ignore[attr-defined]
    # path('<uuid:pk>/generate/', views.generate_report, name='generate-report'),  # type: ignore[attr-defined]
    
    # Templates
    # path('templates/', views.ReportTemplateListCreateView.as_view(), name='template-list-create'),  # type: ignore[attr-defined]
    
    # Dashboards
    # path('dashboards/', views.DashboardListCreateView.as_view(), name='dashboard-list-create'),  # type: ignore[attr-defined]
    # path('dashboards/<uuid:pk>/data/', views.dashboard_data, name='dashboard-data'),  # type: ignore[attr-defined]
    
    # Router URLs
    path('', include(router.urls)),
]
