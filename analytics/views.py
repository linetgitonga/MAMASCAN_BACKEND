# mamascan/analytics/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
from decimal import Decimal
from appointments.models import Appointment, Client, Staff, Service, ClientFeedback
from .models import AnalyticsReport, KPIMetric
from .utils import generate_report_data, calculate_kpis

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
    
    # Key Performance Indicators
    kpis = calculate_kpis(appointments, date_from, date_to)
    
    # Appointments by status
    status_data = list(appointments.values('status').annotate(count=Count('id')))
    
    # Revenue by service
    revenue_data = list(
        appointments.filter(status='completed')
        .values('service__name')
        .annotate(revenue=Sum('service__price'), count=Count('id'))
        .order_by('-revenue')[:10]
    )
    
    # Staff performance
    staff_performance = list(
        appointments.values('staff__first_name', 'staff__last_name')
        .annotate(
            total_appointments=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status__in=['cancelled', 'no_show'])),
            revenue=Sum('service__price', filter=Q(status='completed'))
        )
        .order_by('-total_appointments')
    )
    
    # Daily appointments trend
    daily_trend = []
    current_date = date_from
    while current_date <= date_to:
        daily_count = appointments.filter(appointment_date=current_date).count()
        daily_revenue = appointments.filter(
            appointment_date=current_date, 
            status='completed'
        ).aggregate(total=Sum('service__price'))['total'] or 0
        
        daily_trend.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'appointments': daily_count,
            'revenue': float(daily_revenue)
        })
        current_date += timedelta(days=1)
    
    # Service popularity
    service_popularity = list(
        appointments.values('service__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Client statistics
    client_stats = {
        'total_clients': Client.objects.filter(is_active=True).count(),
        'new_clients': Client.objects.filter(
            created_at__date__range=[date_from, date_to]
        ).count(),
        'repeat_clients': Client.objects.filter(
            appointments__appointment_date__range=[date_from, date_to]
        ).annotate(appointment_count=Count('appointments')).filter(appointment_count__gt=1).count(),
        'active_clients': Client.objects.filter(
            appointments__appointment_date__range=[date_from, date_to]
        ).distinct().count()
    }
    
    # Feedback analysis
    feedback_stats = ClientFeedback.objects.filter(
        appointment__appointment_date__range=[date_from, date_to]
    ).aggregate(
        avg_rating=Avg('rating'),
        avg_service_quality=Avg('service_quality'),
        avg_staff_professionalism=Avg('staff_professionalism'),
        avg_facility_cleanliness=Avg('facility_cleanliness'),
        total_reviews=Count('id'),
        recommend_count=Count('id', filter=Q(would_recommend=True))
    )
    
    # Peak hours analysis
    peak_hours = list(
        appointments.extra(
            select={'hour': 'EXTRACT(hour FROM appointment_time)'}
        ).values('hour').annotate(count=Count('id')).order_by('-count')[:8]
    )
    
    # Monthly comparison (current vs previous month)
    previous_month_start = date_from - timedelta(days=30)
    previous_month_end = date_from - timedelta(days=1)
    
    current_period_stats = appointments.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        revenue=Sum('service__price', filter=Q(status='completed'))
    )
    
    previous_period_stats = Appointment.objects.filter(
        appointment_date__range=[previous_month_start, previous_month_end]
    ).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        revenue=Sum('service__price', filter=Q(status='completed'))
    )
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'kpis': kpis,
        'status_data': json.dumps(status_data),
        'revenue_data': json.dumps(revenue_data),
        'staff_performance': staff_performance,
        'daily_trend': json.dumps(daily_trend),
        'service_popularity': json.dumps(service_popularity),
        'client_stats': client_stats,
        'feedback_stats': feedback_stats,
        'peak_hours': peak_hours,
        'current_period_stats': current_period_stats,
        'previous_period_stats': previous_period_stats,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def revenue_analysis(request):
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = timezone.now().date() - timedelta(days=90)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    completed_appointments = Appointment.objects.filter(
        appointment_date__range=[date_from, date_to],
        status='completed'
    )
    
    # Total revenue
    total_revenue = completed_appointments.aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    # Revenue by service
    revenue_by_service = list(
        completed_appointments.values('service__name', 'service__price')
        .annotate(
            count=Count('id'),
            total_revenue=Sum('service__price')
        ).order_by('-total_revenue')
    )
    
    # Revenue by staff
    revenue_by_staff = list(
        completed_appointments.values('staff__first_name', 'staff__last_name')
        .annotate(
            appointments_completed=Count('id'),
            total_revenue=Sum('service__price'),
            avg_revenue_per_appointment=Avg('service__price')
        ).order_by('-total_revenue')
    )
    
    # Monthly revenue trend
    monthly_revenue = []
    current_date = date_from.replace(day=1)  # Start of month
    
    while current_date <= date_to:
        # Calculate end of month
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        month_end = next_month - timedelta(days=1)
        if month_end > date_to:
            month_end = date_to
        
        month_revenue = completed_appointments.filter(
            appointment_date__range=[current_date, month_end]
        ).aggregate(total=Sum('service__price'))['total'] or 0
        
        month_appointments = completed_appointments.filter(
            appointment_date__range=[current_date, month_end]
        ).count()
        
        monthly_revenue.append({
            'month': current_date.strftime('%Y-%m'),
            'revenue': float(month_revenue),
            'appointments': month_appointments,
            'avg_per_appointment': float(month_revenue / month_appointments) if month_appointments > 0 else 0
        })
        
        current_date = next_month
        if current_date > date_to:
            break
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'revenue_by_service': revenue_by_service,
        'revenue_by_staff': revenue_by_staff,
        'monthly_revenue': json.dumps(monthly_revenue),
    }
    
    return render(request, 'analytics/revenue_analysis.html', context)

@login_required
def staff_performance(request):
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
    
    # Staff performance metrics
    staff_metrics = []
    
    for staff in Staff.objects.filter(is_active=True):
        appointments = Appointment.objects.filter(
            staff=staff,
            appointment_date__range=[date_from, date_to]
        )
        
        total_appointments = appointments.count()
        completed = appointments.filter(status='completed').count()
        cancelled = appointments.filter(status__in=['cancelled', 'no_show']).count()
        
        # Calculate completion rate
        completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
        
        # Calculate revenue
        revenue = appointments.filter(status='completed').aggregate(
            total=Sum('service__price')
        )['total'] or 0
        
        # Get feedback ratings for this staff
        feedback = ClientFeedback.objects.filter(
            appointment__staff=staff,
            appointment__appointment_date__range=[date_from, date_to]
        ).aggregate(
            avg_rating=Avg('staff_professionalism'),
            total_reviews=Count('id')
        )
        
        staff_metrics.append({
            'staff': staff,
            'total_appointments': total_appointments,
            'completed': completed,
            'cancelled': cancelled,
            'completion_rate': round(completion_rate, 1),
            'revenue': revenue,
            'avg_rating': round(feedback['avg_rating'] or 0, 1),
            'total_reviews': feedback['total_reviews'],
            'avg_revenue_per_appointment': revenue / completed if completed > 0 else 0
        })
    
    # Sort by completion rate
    staff_metrics.sort(key=lambda x: x['completion_rate'], reverse=True)
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'staff_metrics': staff_metrics,
    }
    
    return render(request, 'analytics/staff_performance.html', context)

@login_required
def client_analysis(request):
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = timezone.now().date() - timedelta(days=90)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Client segmentation
    clients_with_stats = []
    
    for client in Client.objects.filter(is_active=True):
        appointments = client.appointments.filter(
            appointment_date__range=[date_from, date_to]
        )
        
        total_appointments = appointments.count()
        if total_appointments == 0:
            continue
            
        completed = appointments.filter(status='completed').count()
        cancelled = appointments.filter(status__in=['cancelled', 'no_show']).count()
        
        # Calculate lifetime value
        lifetime_value = appointments.filter(status='completed').aggregate(
            total=Sum('service__price')
        )['total'] or 0
        
        # Get latest appointment
        latest_appointment = appointments.order_by('-appointment_date').first()
        
        clients_with_stats.append({
            'client': client,
            'total_appointments': total_appointments,
            'completed': completed,
            'cancelled': cancelled,
            'lifetime_value': lifetime_value,
            'avg_appointment_value': lifetime_value / completed if completed > 0 else 0,
            'latest_appointment': latest_appointment.appointment_date if latest_appointment else None,
            'completion_rate': (completed / total_appointments * 100) if total_appointments > 0 else 0
        })
    
    # Sort by lifetime value
    clients_with_stats.sort(key=lambda x: x['lifetime_value'], reverse=True)
    
    # Client acquisition analysis
    new_clients_by_month = []
    current_date = date_from.replace(day=1)
    
    while current_date <= date_to:
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        month_end = next_month - timedelta(days=1)
        if month_end > date_to:
            month_end = date_to
        
        new_clients = Client.objects.filter(
            created_at__date__range=[current_date, month_end]
        ).count()
        
        new_clients_by_month.append({
            'month': current_date.strftime('%Y-%m'),
            'new_clients': new_clients
        })
        
        current_date = next_month
        if current_date > date_to:
            break
    
    # Top clients by value
    top_clients = clients_with_stats[:10]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'clients_with_stats': clients_with_stats[:50],  # Limit for display
        'top_clients': top_clients,
        'new_clients_by_month': json.dumps(new_clients_by_month),
        'total_active_clients': len(clients_with_stats),
    }
    
    return render(request, 'analytics/client_analysis.html', context)

@login_required
def feedback_analysis(request):
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = timezone.now().date() - timedelta(days=90)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    feedback_queryset = ClientFeedback.objects.filter(
        appointment__appointment_date__range=[date_from, date_to]
    )
    
    # Overall ratings
    overall_stats = feedback_queryset.aggregate(
        avg_overall=Avg('rating'),
        avg_service_quality=Avg('service_quality'),
        avg_staff_professionalism=Avg('staff_professionalism'),
        avg_facility_cleanliness=Avg('facility_cleanliness'),
        total_reviews=Count('id'),
        recommend_count=Count('id', filter=Q(would_recommend=True))
    )
    
    # Rating distribution
    rating_distribution = list(
        feedback_queryset.values('rating')
        .annotate(count=Count('id'))
        .order_by('rating')
    )
    
    # Feedback by service
    service_feedback = list(
        feedback_queryset.values('appointment__service__name')
        .annotate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
            avg_service_quality=Avg('service_quality')
        ).order_by('-avg_rating')
    )
    
    # Feedback by staff
    staff_feedback = list(
        feedback_queryset.values('appointment__staff__first_name', 'appointment__staff__last_name')
        .annotate(
            avg_rating=Avg('staff_professionalism'),
            total_reviews=Count('id'),
            recommend_rate=Avg('would_recommend') * 100
        ).order_by('-avg_rating')
    )
    
    # Recent feedback comments
    recent_feedback = feedback_queryset.exclude(
        comment__exact=''
    ).order_by('-created_at')[:10]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'overall_stats': overall_stats,
        'rating_distribution': json.dumps(rating_distribution),
        'service_feedback': service_feedback,
        'staff_feedback': staff_feedback,
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'analytics/feedback_analysis.html', context)

@login_required
def export_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_from = datetime.strptime(request.POST.get('date_from'), '%Y-%m-%d').date()
        date_to = datetime.strptime(request.POST.get('date_to'), '%Y-%m-%d').date()
        
        # Generate report data
        report_data = generate_report_data(report_type, date_from, date_to)
        
        # Create report record
        report = AnalyticsReport.objects.create(
            name=f"{report_type.title()} Report - {date_from} to {date_to}",
            report_type=report_type,
            date_from=date_from,
            date_to=date_to,
            generated_by=request.user,
            data=report_data
        )
        
        return JsonResponse({
            'success': True,
            'report_id': report.id,
            'message': 'Report generated successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
