# backend/curation/urls.py
from django.urls import path
from .views import InterestListView, UserInterestView

urlpatterns = [
    path('interests/', InterestListView.as_view(), name='interest-list'),
    path('user-interests/', UserInterestView.as_view(), name='user-interest'),
]