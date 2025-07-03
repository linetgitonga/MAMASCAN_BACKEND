from django.urls import path
from .views import initiate_payment_view, payment_callback, payment_status
urlpatterns = [
    path('initiate-payment/', initiate_payment_view, name='initiate_payment'),
    # path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path('payment-callback/', payment_callback, name='payment_callback'),
    path('payment-status/<str:transaction_id>/', payment_status, name='payment_status'),
]