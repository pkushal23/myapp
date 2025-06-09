# backend/curation/admin.py
from django.contrib import admin
from .models import Interest, UserInterest, Article, Newsletter

admin.site.register(Interest)
admin.site.register(UserInterest)
admin.site.register(Article) # Register Article
admin.site.register(Newsletter) # Register Newsletter