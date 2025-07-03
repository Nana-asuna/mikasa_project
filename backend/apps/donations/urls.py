from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Donors
    path('donors/', views.DonorListCreateView.as_view(), name='donor-list-create'),
    path('donors/<uuid:pk>/', views.DonorDetailView.as_view(), name='donor-detail'),
    
    # Donations
    path('', views.DonationListCreateView.as_view(), name='donation-list-create'),
    path('<uuid:pk>/', views.DonationDetailView.as_view(), name='donation-detail'),
    path('statistics/', views.donation_statistics, name='donation-statistics'),
    
    # Campaigns
    path('campaigns/', views.DonationCampaignListCreateView.as_view(), name='campaign-list-create'),
    
    # Router URLs
    path('', include(router.urls)),
]
