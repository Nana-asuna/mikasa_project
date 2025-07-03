from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Children management
    path('', views.ChildListCreateView.as_view(), name='child-list-create'),
    path('<uuid:pk>/', views.ChildDetailView.as_view(), name='child-detail'),
    path('public/', views.PublicChildrenView.as_view(), name='public-children'),
    path('statistics/', views.children_statistics, name='children-statistics'),
    
    # Child-related data
    path('<uuid:child_id>/notes/', views.ChildNotesView.as_view(), name='child-notes'),
    path('<uuid:child_id>/documents/', views.ChildDocumentsView.as_view(), name='child-documents'),
    path('<uuid:child_id>/medical-records/', views.MedicalRecordsView.as_view(), name='medical-records'),
    
    # Router URLs
    path('', include(router.urls)),
]
