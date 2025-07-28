from django.shortcuts import render, redirect
from events.forms import EventForm, EventModelForm, EventDetailModelForm
from events.models import Event, EventDetail, Project
from datetime import date
from django.db.models import Q, Count, Max, Min, Avg
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.utils.decorators import method_decorator
from django.views import View
from users.views import is_admin


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_employee(user):
    return user.groups.filter(name='Manager').exists()

@method_decorator(user_passes_test(is_manager, login_url='no-permission'), name='dispatch')
class manager_dashboard(View):
    template_name = "dashboard/manager-dashboard.html"

    def get(self, request):
        event_type = request.GET.get('type', 'all')

        counts = Event.objects.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            pending=Count('id', filter=Q(status='PENDING')),
        )

        base_query = Event.objects.select_related('details').prefetch_related('assigned_to')

        if event_type == 'completed':
            events = base_query.filter(status='COMPLETED')
        elif event_type == 'in-progress':
            events = base_query.filter(status='IN_PROGRESS')
        elif event_type == 'pending':
            events = base_query.filter(status='PENDING')
        else:
            events = base_query.all()

        context = {
            "events": events,
            "counts": counts,
            "role": 'manager'
        }
        return render(request, self.template_name, context)


@method_decorator(user_passes_test(is_employee), name='dispatch')
class employee_dashboard(View):
    template_name = "dashboard/user-dashboard.html"

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required("event.add_task", login_url='no-permission'), name='dispatch')
class create_event(View):
    template_name = "event_form.html"

    def get(self, request):
        event_form = EventModelForm()
        event_detail_form = EventDetailModelForm()
        context = {
            "event_form": event_form,
            "event_detail_form": event_detail_form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        event_form = EventModelForm(request.POST)
        event_detail_form = EventDetailModelForm(request.POST, request.FILES)

        if event_form.is_valid() and event_detail_form.is_valid():

            event = event_form.save()
            event_detail = event_detail_form.save(commit=False)
            event_detail.event = event
            event_detail.save()

            messages.success(request, "Event Created Successfully")
            return redirect('create-event')

        context = {
            "event_form": event_form,
            "event_detail_form": event_detail_form
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required("event.change_event", login_url='no-permission'), name='dispatch')
class update_event(View):
    template_name = "event_form.html"

    def get(self, request, id):
        event = Event.objects.get(id=id)
        event_form = EventModelForm(instance=event)
        event_detail_form = EventDetailModelForm(instance=event.details) if event.details else None

        context = {
            "event_form": event_form,
            "event_detail_form": event_detail_form
        }
        return render(request, self.template_name, context)

    def post(self, request, id):
        event = Event.objects.get(id=id)
        event_form = EventModelForm(request.POST, instance=event)
        event_detail_form = EventDetailModelForm(request.POST, instance=event.details)

        if event_form.is_valid() and event_detail_form.is_valid():
            event = event_form.save()
            event_detail = event_detail_form.save(commit=False)
            event_detail.event = event
            event_detail.save()

            messages.success(request, "Event Updated Successfully")
            return redirect('update-event', id=id)

        context = {
            "event_form": event_form,
            "event_detail_form": event_detail_form
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required("events.delete_event", login_url='no-permission'), name='dispatch')
class delete_event(View):
    def post(self, request, id):
        event = Event.objects.get(id=id)
        event.delete()
        messages.success(request, 'Event Deleted Successfully')
        return redirect('manager-dashboard')

    def get(self, request, id):
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required("events.view_event", login_url='no-permission'), name='dispatch')
class view_event(View):
    template_name = "show_event.html"

    def get(self, request):
        projects = Project.objects.annotate(
            num_event=Count('event')
        ).order_by('num_event')

        return render(request, self.template_name, {"projects": projects})

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required("events.view_event", login_url='no-permission'), name='dispatch')
class event_details(View):
    template_name = 'event_details.html'

    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        status_choices = Event.STATUS_CHOICES
        return render(request, self.template_name, {
            "event": event,
            "status_choices": status_choices
        })

    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)
        selected_status = request.POST.get('event_status')
        event.status = selected_status
        event.save()
        return redirect('event-details', event.id)



@method_decorator(login_required, name='dispatch')
class dashboard(View):
    def get(self, request):
        user = request.user

        if is_manager(user):
            return redirect('manager-dashboard')
        elif is_employee(user):
            return redirect('user-dashboard')
        elif is_admin(user):
            return redirect('admin-dashboard')

        return redirect('no-permission')

       
