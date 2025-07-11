from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from .models import FundiProfile, User
from .serializers import FundiProfileSerializer
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from payments.models import Payment


class RegisterView(APIView):
    """
    Register a new user (fundi or client).
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Login for fundis or clients. Returns authentication token.
    """
    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(request, phone_number=phone, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)


class FundiProfileView(APIView):
    """
    Get or update the authenticated fundi's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)
        profile = request.user.fundi_profile
        serializer = FundiProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)
        profile = request.user.fundi_profile
        serializer = FundiProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class FundiDeleteView(APIView):
    """
    Delete the authenticated fundi's account.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)
        request.user.delete()
        return Response({"message": "Account deleted"}, status=204)



class FundiPublicList(APIView):
    """
    List all visible fundis (on trial or subscribed in the last 30 days).
    """
    def get(self, request):
        now = timezone.now()
        profiles = FundiProfile.objects.select_related('user').filter(user__role='fundi')
        visible_fundis = []

        for profile in profiles:
            user = profile.user

            # ✅ 1. If still on trial, and trial is not expired
            if user.on_trial and user.trial_ends and user.trial_ends >= now:
                visible_fundis.append(profile)
                continue

            # ✅ 2. If trial has expired, deactivate on_trial
            if user.on_trial and user.trial_ends and user.trial_ends < now:
                user.on_trial = False
                user.save()

            # ✅ 3. Check if payment was made in the last 30 days
            last_payment = Payment.objects.filter(
                user=user,
                purpose='subscription',
                status='Completed'
            ).order_by('-created_at').first()

            if last_payment and (now - last_payment.created_at) <= timedelta(days=30):
                visible_fundis.append(profile)

        data = []
        for profile in visible_fundis:
            data.append({
                "id": profile.user.id,
                "name": profile.user.name,
                "skills": profile.skills,
                "location": profile.location,
                "rate_note": profile.rate_note,
                "is_available": profile.is_available,
                "phone_number": profile.user.phone_number if profile.show_contact else None,
            })
        return Response(data)

class FundiPublicDetail(APIView):
    """
    Retrieve public info for a specific fundi.
    """
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk, role='fundi')
        profile = user.fundi_profile
        data = {
            "id": user.id,
            "name": user.name,
            "skills": profile.skills,
            "location": profile.location,
            "rate_note": profile.rate_note,
            "is_available": profile.is_available,
            "phone_number": user.phone_number if profile.show_contact else None,
        }
        return Response(data)


class ClientRegisterView(generics.CreateAPIView):
    """
    Register a new client.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class ClientLoginView(APIView):
    """
    Login for client. Returns authentication token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = User.objects.filter(phone_number=phone_number, role='client').first()
        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ClientListView(generics.ListAPIView):
    """
    Publicly list all registered clients.
    """
    queryset = User.objects.filter(role='client')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class ClientMeView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete authenticated client account.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

