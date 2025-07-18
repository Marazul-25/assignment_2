from django.urls import path
from events.views import manager_dashboard, employee_dashboard, create_event, view_event, update_event, delete_event, event_details, dashboard

urlpatterns = [
    path('manager-dashboard/', manager_dashboard, name="manager-dashboard"),
    path('user-dashboard/', employee_dashboard, name='user-dashboard'),
    path('create-event/', create_event, name='create-event'),
    path('view_event/', view_event),
    path('event/<int:event_id>/details/', event_details, name='event-details'),
    path('update-event/<int:id>/', update_event, name='update-event'),
    path('delete-event/<int:id>/', delete_event, name='delete-event'),
    path('dashboard', dashboard, name='dashboard')
]