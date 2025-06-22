from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import Appointment, Client, Staff, Service, ClientFeedback
from .forms import AppointmentForm, ClientForm, FeedbackForm

@login_required
def dashboard(request):
    today = timezone.now().date()
    
    # Basic stats
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(status='scheduled').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('client', 'staff', 'service').order_by('-created_at')[:5]
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        status__in=['scheduled', 'confirmed']
    ).select_related('client', 'staff', 'service').order_by('appointment_date', 'appointment_time')[:10]
    
    context = {
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'recent_appointments': recent_appointments,
        'upcoming_appointments': upcoming_appointments,
    }
    
    return render(request, 'appointments/dashboard.html', context)

@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related('client', 'staff', 'service').order_by('-appointment_date', '-appointment_time')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        appointments = appointments.filter(appointment_date__gte=date_from)
    if date_to:
        appointments = appointments.filter(appointment_date__lte=date_to)
    
    # Filter by staff
    staff_id = request.GET.get('staff')
    if staff_id:
        appointments = appointments.filter(staff_id=staff_id)
    
    context = {
        'appointments': appointments,
        'staff_list': Staff.objects.filter(is_active=True),
        'status_choices': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, 'Appointment created successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Create Appointment'})

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check if feedback exists
    try:
        feedback = appointment.clientfeedback
    except ClientFeedback.DoesNotExist:
        feedback = None
    
    context = {
        'appointment': appointment,
        'feedback': feedback,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def appointment_update_status(request, pk):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Appointment.STATUS_CHOICES):
            old_status = appointment.status
            appointment.status = new_status
            appointment.save()
            
            # Create history record
            AppointmentHistory.objects.create(
                appointment=appointment,
                previous_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                notes=request.POST.get('notes', '')
            )
            
            messages.success(request, f'Appointment status updated to {new_status}')
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def analytics_dashboard(request):
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = timezone.now().date() - timedelta(days=30)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Base queryset
    appointments = Appointment.objects.filter(appointment_date__range=[date_from, date_to])
    
    # Key metrics
    total_appointments = appointments.count()
    completion_rate = 0
    if total_appointments > 0:
        completed = appointments.filter(status='completed').count()
        completion_rate = (completed / total_appointments) * 100
    
    cancellation_rate = 0
    if total_appointments > 0:
        cancelled = appointments.filter(status__in=['cancelled', 'no_show']).count()
        cancellation_rate = (cancelled / total_appointments) * 100
    
    # Revenue calculation
    revenue = appointments.filter(status='completed').aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    # Appointments by status
    status_data = appointments.values('status').annotate(count=Count('id'))
    
    # Appointments by service
    service_data = appointments.values('service__name').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Appointments by staff
    staff_data = appointments.values('staff__first_name', 'staff__last_name').annotate(count=Count('id')).order_by('-count')
    
    # Daily appointments trend
    daily_data = []
    current_date = date_from
    while current_date <= date_to:
        daily_count = appointments.filter(appointment_date=current_date).count()
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': daily_count
        })
        current_date += timedelta(days=1)
    
    # Client feedback analysis
    feedback_data = ClientFeedback.objects.filter(
        appointment__appointment_date__range=[date_from, date_to]
    ).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        recommend_count=Count('id', filter=Q(would_recommend=True))
    )
    
    # Peak hours analysis
    peak_hours = appointments.extra(
        select={'hour': 'EXTRACT(hour FROM appointment_time)'}
    ).values('hour').annotate(count=Count('id')).order_by('-count')[:5]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_appointments': total_appointments,
        'completion_rate': round(completion_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'revenue': revenue,
        'status_data': json.dumps(list(status_data)),
        'service_data': json.dumps(list(service_data)),
        'staff_data': list(staff_data),
        'daily_data': json.dumps(daily_data),
        'feedback_data': feedback_data,
        'peak_hours': list(peak_hours),
    }
    
    return render(request, 'appointments/analytics.html', context)

@login_required
def client_list(request):
    clients = Client.objects.all().order_by('first_name', 'last_name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        clients = clients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    return render(request, 'appointments/client_list.html', {'clients': clients})

@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, 'Client created successfully!')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    return render(request, 'appointments/client_form.html', {'form': form, 'title': 'Create Client'})

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    appointments = client.appointment_set.all().order_by('-appointment_date', '-appointment_time')
    
    # Client statistics
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    cancelled_appointments = appointments.filter(status__in=['cancelled', 'no_show']).count()
    
    context = {
        'client': client,
        'appointments': appointments[:10],  # Last 10 appointments
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
    }
    
    return render(request, 'appointments/client_detail.html', context)
