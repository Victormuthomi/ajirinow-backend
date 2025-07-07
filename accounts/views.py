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
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)


# GET or UPDATE own profile
class FundiProfileView(APIView):
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


# DELETE fundi account
class FundiDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)
        request.user.delete()
        return Response({"message": "Account deleted"}, status=204)


# Public: List all fundis
class FundiPublicList(APIView):
    def get(self, request):
        profiles = FundiProfile.objects.filter(user__role='fundi')
        data = []
        for profile in profiles:
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


# Public: View single fundi
class FundiPublicDetail(APIView):
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


# Client Registration View
class ClientRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]



# Client Login View
class ClientLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = User.objects.filter(phone_number=phone_number, role='client').first()
        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# List All Clients
class ClientListView(generics.ListAPIView):
    queryset = User.objects.filter(role='client')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# Logged-In Client: View, Update, Delete
class ClientMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
