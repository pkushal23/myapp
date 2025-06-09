 # backend/accounts/urls.py
from django.urls import path
from .views import RegisterAPI, LoginAPI, UserAPI, LogoutAPI

urlpatterns = [
        path('register/', RegisterAPI.as_view(), name='register'),
        path('login/', LoginAPI.as_view(), name='login'),
        path('user/', UserAPI.as_view(), name='user_info'),
        path('logout/', LogoutAPI.as_view(), name='logout'),
    ]