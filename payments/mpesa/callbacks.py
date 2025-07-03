from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from payments.models import Payment, Transaction

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            amount = data.get('amount')
            status = data.get('status')

            # Update the payment status in the database
            payment = Payment.objects.get(id=transaction_id)
            payment.status = status
            payment.save()

            # Create a transaction record
            Transaction.objects.create(
                payment=payment,
                transaction_id=transaction_id,
                amount=amount,
                status=status
            )

            return JsonResponse({'message': 'Callback processed successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)