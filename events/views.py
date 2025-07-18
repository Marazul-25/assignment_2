from django.shortcuts import render, redirect
from django.http import HttpResponse
from events.forms import EventForm, EventModelForm, EventDetailModelForm
from events.models import Event, EventDetail, Project
from datetime import date
from django.db.models import Q, Count, Max, Min, Avg
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_employee(user):
    return user.groups.filter(name='Manager').exists()


@user_passes_test(is_manager, login_url='no-permission')
def manager_dashboard(request):
    type = request.GET.get('type', 'all')

    counts = Event.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='COMPLETED')),
        in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
        pending=Count('id', filter=Q(status='PENDING')),
    )


    base_query = Event.objects.select_related(
        'details').prefetch_related('assigned_to')

    if type == 'completed':
        events = base_query.filter(status='COMPLETED')
    elif type == 'in-progress':
        events = base_query.filter(status='IN_PROGRESS')
    elif type == 'pending':
        events = base_query.filter(status='PENDING')
    elif type == 'all':
        events = base_query.all()

    context = {
        "events": events,
        "counts": counts,
        "role": 'manager'
    }
    return render(request, "dashboard/manager-dashboard.html", context)


@user_passes_test(is_employee)
def employee_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


@login_required
@permission_required("event.add_task", login_url='no-permission')
def create_task(request):
    event_form = EventModelForm() 
    event_detail_form = EventDetailModelForm()

    if request.method == "POST":
        event_form = EventModelForm(request.POST)
        event_detail_form = EventDetailModelForm(request.POST, request.FILES)

        if event_form.is_valid() and event_detail_form.is_valid():

            event = event_form.save()
            event_detail = event_detail_form.save(commit=False)
            event_detail.event = event
            event_detail.save()

            messages.success(request, "Event Created Successfully")
            return redirect('create-event')

    context = {"event_form": event_form, "event_detail_form":event_detail_form}
    return render(request, "event_form.html", context)


@login_required
@permission_required("tasks.change_task", login_url='no-permission')
def update_event(request, id):
    event = Event.objects.get(id=id)
    event_form = EventModelForm(instance=event)  

    if event.details:
        event_detail_form = EventDetailModelForm(instance=event.details)

    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        event_detail_form = EventDetailModelForm(
            request.POST, instance=event.details)

        if event_form.is_valid() and event_detail_form.is_valid():
            event = event_form.save()
            event_detail = event_detail_form.save(commit=False)
            event_detail.event = event
            event_detail.save()

            messages.success(request, "Event Updated Successfully")
            return redirect('update-event', id)

    context = {"event_form": event_form, "event_detail_form": event_detail_form}
    return render(request, "event_form.html", context)


@login_required
@permission_required("events.delete_event", login_url='no-permission')
def delete_event(request, id):
    if request.method == 'POST':
        event = Event.objects.get(id=id)
        event.delete()
        messages.success(request, 'Event Deleted Successfully')
        return redirect('manager-dashboard')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')


@login_required
@permission_required("events.view_event", login_url='no-permission')
def view_event(request):
    projects = Project.objects.annotate(
        num_event=Count('event')).order_by('num_event')
    return render(request, "show_event.html", {"projects": projects})


@login_required
@permission_required("events.view_event", login_url='no-permission')
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    status_choices = Event.STATUS_CHOICES

    if request.method == 'POST':
        selected_status = request.POST.get('event_status')
        print(selected_status)
        event.status = selected_status
        event.save()
        return redirect('event-details', event.id)

    return render(request, 'event_details.html', {"event": event, 'status_choices': status_choices})


@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')

    return redirect('no-permission')