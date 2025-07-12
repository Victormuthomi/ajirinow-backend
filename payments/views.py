from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


from payments.models import Payment
from jobs.models import Job
from ads.models import Ad
from accounts.models import User
from django.utils import timezone
from datetime import timedelta


class STKPushView(APIView):
    """
    POST: Initiate M-Pesa STK Push

    Required:
    - phone: Phone number in format 2547XXXXXXXX
    - amount: Integer amount to charge
    - purpose: One of ['subscription', 'post_job', 'post_ad']

    Returns:
    - M-Pesa API response and logs payment as pending
    - For 'post_job', attempts to activate the most recent unpaid job
    """
    def post(self, request):
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        purpose = request.data.get("purpose")

        if not phone or not amount or not purpose:
            return Response({"error": "Phone, amount, and purpose are required"}, status=400)

        if purpose not in ['subscription', 'post_job', 'post_ad']:
            return Response({"error": "Invalid purpose"}, status=400)

        try:
            result = lipa_na_mpesa_online(phone, int(amount))

            if result.get("ResponseCode") == "0":
                user = request.user if request.user.is_authenticated else None

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

                if purpose == "post_job" and user:
                    job = Job.objects.filter(
                        client=user, is_active=False, payment__isnull=True
                    ).order_by('-created_at').first()
                    if job:
                        job.payment = payment
                        job.is_active = True
                        job.expires_at = timezone.now() + timedelta(weeks=12)
                        job.save()

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
def mpesa_callback(request):
    """
    M-Pesa Callback Endpoint (Safaricom calls this)

    Automatically:
    - Marks payment as 'Completed' or 'Failed'
    - Activates job or ad if payment purpose matches and is valid
    """
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

        if result_code == 0:  # Success
            items = body.get('CallbackMetadata', {}).get('Item', [])
            amount = next((item['Value'] for item in items if item['Name'] == 'Amount'), 0)

            payment.status = 'Completed'
            payment.amount = amount
            payment.save()

            if payment.purpose == 'post_job':
                job = Job.objects.filter(client=payment.user, payment=payment).first()
                if job:
                    job.is_active = True
                    job.expires_at = timezone.now() + timedelta(weeks=12)
                    job.save()

            elif payment.purpose == 'post_ad':
                ad = Ad.objects.filter(
                    client=payment.user, is_active=False, payment__isnull=True
                ).order_by('-created_at').first()
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
        pass  # Optionally log this

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_payment_status(request):
    job_id = request.GET.get("job_id")
    if not job_id:
        return Response({"error": "job_id is required"}, status=400)

    try:
        job = Job.objects.get(id=job_id, client=request.user)

        if job.payment:
            return Response({
                "status": job.payment.status,
                "purpose": job.payment.purpose,
                "post_expiry_date": job.payment.post_expiry_date,
            })
        else:
            return Response({"status": "Pending"})

    except Job.DoesNotExist:
        return Response({"status": "NotFound"}, status=404)

