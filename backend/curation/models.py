# backend/curation/models.py
from django.db import models
from django.contrib.auth.models import User # Import Django's built-in User model

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Interests" # Fixes plural name in admin

    def __str__(self):
        return self.name

class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_interests')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    # You could add 'strength' or 'priority' fields here later if needed

    class Meta:
        unique_together = ('user', 'interest') # A user can only have an interest once

    def __str__(self):
        return f"{self.user.username}'s interest in {self.interest.name}"



class Article(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=500, unique=True)
    source = models.CharField(max_length=100)
    published_date = models.DateTimeField()
    summary = models.TextField(blank=True, null=True) # AI-generated summary
    full_text = models.TextField(blank=True, null=True) # Optional, store full text for AI processing if needed
    topics = models.ManyToManyField(Interest, related_name='articles') # Relate to interests

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

class Newsletter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='newsletters')
    generation_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField() # The full AI-generated newsletter text
    articles_included = models.ManyToManyField(Article, related_name='newsletters') # Articles summarized in this newsletter

    class Meta:
        ordering = ['-generation_date']

    def __str__(self):
        return f"Newsletter for {self.user.username} on {self.generation_date.strftime('%Y-%m-%d')}"