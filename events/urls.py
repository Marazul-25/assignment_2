from django.urls import path
from events.views import manager_dashboard, employee_dashboard, create_event, view_event, update_event, delete_event, event_details, dashboard

urlpatterns = [
    path('manager-dashboard/', manager_dashboard.as_view(), name="manager-dashboard"),
    path('user-dashboard/', employee_dashboard.as_view(), name='user-dashboard'),
    path('create-event/', create_event.as_view(), name='create-event'),
    path('view_event/', view_event.as_view(),name='event-view'),
    path('event/<int:event_id>/details/', event_details.as_view(), name='event-details'),
    path('update-event/<int:id>/', update_event.as_view(), name='update-event'),
    path('delete-event/<int:id>/', delete_event.as_view(), name='delete-event'),
    path('dashboard', dashboard.as_view(), name='dashboard')
]
