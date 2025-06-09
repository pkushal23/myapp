# backend/accounts/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import logout
from .serializers import UserSerializer, RegisterSerializer

class RegisterAPI(generics.GenericAPIView):
        serializer_class = RegisterSerializer

        def post(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token.key
            })

class LoginAPI(ObtainAuthToken):
        def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })

class UserAPI(generics.RetrieveAPIView):
        permission_classes = [permissions.IsAuthenticated]
        serializer_class = UserSerializer

        def get_object(self):
            return self.request.user

class LogoutAPI(APIView):
        permission_classes = [permissions.IsAuthenticated]

        def post(self, request):
            request.user.auth_token.delete() # Delete the user's token
            logout(request)
            return Response(status=204) # No Content