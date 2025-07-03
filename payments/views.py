from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Payment
from .serializers import PaymentSerializer
from .utils import generate_payment_link, validate_payment_response
# from .mpesa.mpesa_services import initiate_payment, check_payment_status
from .mpesa.mpesa_services import MpesaService


@api_view(['POST'])
def create_payment(request):
    amount = request.data.get('amount')
    service_id = request.data.get('service_id')
    
    payment_link = generate_payment_link(amount, service_id)
    
    # Here you would typically save the payment to the database
    payment = Payment(amount=amount, status='PENDING', user=request.user)
    payment.save()
    
    return JsonResponse({'payment_link': payment_link})

@api_view(['POST'])
def payment_callback(request):
    response = request.data
    
    if validate_payment_response(response):
        payment = Payment.objects.get(id=response['id'])
        payment.status = response['status']
        payment.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'failure'}, status=400)

@api_view(['GET'])
def payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        return JsonResponse({'status': payment.status, 'amount': payment.amount})
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    

@api_view(['POST'])
def initiate_payment_view(request):
    amount = request.data.get('amount')
    phone_number = request.data.get('phone_number')
    mpesa = MpesaService()
    response = mpesa.initiate_payment(amount, phone_number)
    return JsonResponse(response)