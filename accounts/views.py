from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, FundiProfileSerializer
from .models import FundiProfile, User
from django.shortcuts import get_object_or_404


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(request, phone_number=phone, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)


class FundiProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)

        user = request.user
        profile = user.fundi_profile

        return Response({
            "name": user.name,
            "phone_number": user.phone_number,
            "id_number": user.id_number,
            "on_trial": user.is_on_trial,
            "is_subscribed": user.is_subscribed,
            "trial_ends": user.trial_ends,
            "subscription_end": user.subscription_end,
            "skills": profile.skills,
            "location": profile.location,
            "rate_note": profile.rate_note,
            "is_available": profile.is_available,
            "show_contact": profile.show_contact,
        })

    def put(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)

        user = request.user
        profile = user.fundi_profile

        user.name = request.data.get("name", user.name)
        user.id_number = request.data.get("id_number", user.id_number)
        user.save()

        serializer = FundiProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundiDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)
        request.user.delete()
        return Response({"message": "Account deleted"}, status=204)


class FundiPublicList(APIView):
    def get(self, request):
        profiles = FundiProfile.objects.select_related('user').filter(user__role='fundi')
        visible_fundis = [
            profile for profile in profiles
            if profile.user.is_on_trial or profile.user.is_subscribed
        ]

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
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk, role='fundi')
        profile = user.fundi_profile
        return Response({
            "id": user.id,
            "name": user.name,
            "skills": profile.skills,
            "location": profile.location,
            "rate_note": profile.rate_note,
            "is_available": profile.is_available,
            "phone_number": user.phone_number if profile.show_contact else None,
        })


class ResetPasswordView(APIView):
    def post(self, request):
        phone = request.data.get("phone_number")
        id_number = request.data.get("id_number")
        new_password = request.data.get("new_password")

        if not (phone and id_number and new_password):
            return Response({"error": "All fields are required"}, status=400)

        try:
            user = User.objects.get(phone_number=phone, id_number=id_number)
            user.password = make_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "Invalid phone number or ID number"}, status=400)


class ClientRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class ClientLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = User.objects.filter(phone_number=phone_number, role='client').first()
        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ClientListView(generics.ListAPIView):
    queryset = User.objects.filter(role='client')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class ClientMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

