# backend/curation/urls.py
from django.urls import path
from .views import InterestListView, UserInterestView, ArticleListView, UserNewsletterListView

urlpatterns = [
    path('interests/', InterestListView.as_view(), name='interest-list'),
    path('user-interests/', UserInterestView.as_view(), name='user-interest'),
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('user-newsletters/', UserNewsletterListView.as_view(), name='user-newsletter-list'),
]