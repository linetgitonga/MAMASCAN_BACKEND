# mamascan/analytics/utils.py
from django.db.models import Count, Sum, Avg, Q
from appointments.models import Appointment, ClientFeedback
from decimal import Decimal

def calculate_kpis(appointments, date_from, date_to):
    """Calculate Key Performance Indicators"""
    total_appointments = appointments.count()
    
    if total_appointments == 0:
        return {
            'total_appointments': 0,
            'completion_rate': 0,
            'cancellation_rate': 0,
            'no_show_rate': 0,
            'total_revenue': 0,
            'avg_appointment_value': 0,
            'client_satisfaction': 0
        }
    
    completed = appointments.filter(status='completed').count()
    cancelled = appointments.filter(status='cancelled').count()
    no_show = appointments.filter(status='no_show').count()
    
    completion_rate = (completed / total_appointments) * 100
    cancellation_rate = (cancelled / total_appointments) * 100
    no_show_rate = (no_show / total_appointments) * 100
    
    total_revenue = appointments.filter(status='completed').aggregate(
        total=Sum('service__price')
    )['total'] or Decimal('0')
    
    avg_appointment_value = total_revenue / completed if completed > 0 else Decimal('0')
    
    # Client satisfaction from feedback
    feedback_avg = ClientFeedback.objects.filter(
        appointment__appointment_date__range=[date_from, date_to]
    ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    return {
        'total_appointments': total_appointments,
        'completion_rate': round(completion_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'no_show_rate': round(no_show_rate, 1),
        'total_revenue': float(total_revenue),
        'avg_appointment_value': float(avg_appointment_value),
        'client_satisfaction': round(feedback_avg, 1)
    }

def generate_report_data(report_type, date_from, date_to):
    """Generate report data based on type"""
    appointments = Appointment.objects.filter(appointment_date__range=[date_from, date_to])
    
    if report_type == 'appointments':
        return {
            'summary': calculate_kpis(appointments, date_from, date_to),
            'by_status': list(appointments.values('status').annotate(count=Count('id'))),
            'by_service': list(appointments.values('service__name').annotate(count=Count('id')).order_by('-count'))
        }
    
    elif report_type == 'revenue':
        completed = appointments.filter(status='completed')
        return {
            'total_revenue': float(completed.aggregate(total=Sum('service__price'))['total'] or 0),
            'by_service': list(completed.values('service__name').annotate(
                revenue=Sum('service__price'), count=Count('id')
            ).order_by('-revenue')),
            'by_staff': list(completed.values('staff__first_name', 'staff__last_name').annotate(
                revenue=Sum('service__price')
            ).order_by('-revenue'))
        }
    # Add more report types as needed
    return {}
