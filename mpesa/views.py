from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .utils import lipa_na_mpesa_online
from payments.models import Payment
from jobs.models import Job
from accounts.models import User
from ads.models import Ad

# Amounts per purpose
PURPOSE_AMOUNTS = {
    "subscription": 200,
    "post_job": 100,
    "post_ad": 500,
}

class STKPushView(APIView):
    """
    POST: Initiates an STK Push to the user's phone using M-Pesa.
    
    Required fields:
    - purpose: "subscription", "post_job", or "post_ad"
    - phone: phone number to send the push to

    Returns:
    - checkout_id and payment_id if successful
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        purpose = request.data.get("purpose")
        phone = request.data.get("phone")

        if not phone or not purpose:
            return Response({"error": "Phone and purpose are required"}, status=400)

        if purpose not in PURPOSE_AMOUNTS:
            return Response({"error": "Invalid purpose"}, status=400)

        # Format phone
        if phone.startswith("0"):
            phone = "254" + phone[1:]

        amount = PURPOSE_AMOUNTS[purpose]

        try:
            result = lipa_na_mpesa_online(phone, amount)

            if result.get("ResponseCode") == "0":
                payment = Payment.objects.create(
                    user=user,
                    phone=phone,
                    amount=amount,
                    merchant_request_id=result["MerchantRequestID"],
                    checkout_request_id=result["CheckoutRequestID"],
                    status="Pending",
                    description=result.get("CustomerMessage", ""),
                    purpose=purpose,
                )

                return Response({
                    "message": "STK push sent",
                    "checkout_id": result["CheckoutRequestID"],
                    "payment_id": payment.id,
                })

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
def mpesa_callback(request):
    data = request.data
    body = data.get('Body', {}).get('stkCallback', {})
    merchant_request_id = body.get('MerchantRequestID')
    checkout_request_id = body.get('CheckoutRequestID')
    result_code = body.get('ResultCode')
    result_desc = body.get('ResultDesc')

    try:
        payment = Payment.objects.get(
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id
        )

        if result_code == 0:
            # ✅ Set payment as completed — DO THIS HERE!
            amount = next(
                (item['Value'] for item in body.get('CallbackMetadata', {}).get('Item', []) if item['Name'] == 'Amount'),
                payment.amount
            )
            payment.amount = amount
            payment.status = 'Completed'
            payment.description = result_desc
            payment.save()

            # ❗️DO NOT manually set user.is_subscribed here

            # Activate stuff based on purpose
            if payment.purpose == 'subscription' and payment.user.role == 'fundi':
                # No need to do anything — user.is_subscribed is calculated
                pass

            elif payment.purpose == 'post_job':
                job = Job.objects.filter(
                    client=payment.user,
                    is_active=False,
                    payment__isnull=True
                ).order_by('-created_at').first()
                if job:
                    job.payment = payment
                    job.is_active = True
                    job.expires_at = timezone.now() + timedelta(weeks=12)
                    job.save()

            elif payment.purpose == 'post_ad':
                ad = Ad.objects.filter(client=payment.user, is_active=False, payment__isnull=True).order_by('-created_at').first()
                if ad:
                    ad.payment = payment
                    ad.is_active = True
                    ad.expires_at = timezone.now() + timedelta(days=7)
                    ad.save()

        else:
            payment.status = 'Failed'
            payment.description = result_desc
            payment.save()

    except Payment.DoesNotExist:
        pass

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

