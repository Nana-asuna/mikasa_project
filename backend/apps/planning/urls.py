from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    # Events
    path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
    path('events/<uuid:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/calendar/', views.calendar_events, name='calendar-events'),
    
    # Tasks
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    
    # Shifts
    path('shifts/', views.ShiftListCreateView.as_view(), name='shift-list-create'),
    
    # Statistics
    path('statistics/', views.planning_statistics, name='planning-statistics'),
    
    # Router URLs
    path('', include(router.urls)),
]
