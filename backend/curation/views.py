# backend/curation/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Interest, UserInterest, Article, Newsletter
from .serializers import InterestSerializer, UserInterestSerializer, UserInterestsUpdateSerializer, NewsletterSerializer
from .serializers import ArticleSerializer
class InterestListView(generics.ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow anyone to see available interests

from rest_framework.views import APIView  # Use this instead for full flexibility

class UserInterestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        interests = UserInterest.objects.filter(user=request.user)
        serializer = UserInterestSerializer(interests, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = UserInterestsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_interests_ids = serializer.validated_data.get('add_interests', [])
        remove_interests_ids = serializer.validated_data.get('remove_interests', [])

        user = request.user
        added_count = 0
        removed_count = 0

        with transaction.atomic():
            for interest_id in add_interests_ids:
                try:
                    interest = Interest.objects.get(id=interest_id)
                    user_interest, created = UserInterest.objects.get_or_create(user=user, interest=interest)
                    if created:
                        added_count += 1
                except Interest.DoesNotExist:
                    return Response({"error": f"Interest with ID {interest_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

            for interest_id in remove_interests_ids:
                try:
                    interest = Interest.objects.get(id=interest_id)
                    deleted_count, _ = UserInterest.objects.filter(user=user, interest=interest).delete()
                    removed_count += deleted_count
                except Interest.DoesNotExist:
                    return Response({"error": f"Interest with ID {interest_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

        current = UserInterest.objects.filter(user=request.user)
        return Response({
            "message": f"Successfully added {added_count} interests and removed {removed_count} interests.",
            "current_interests": UserInterestSerializer(current, many=True).data
        }, status=status.HTTP_200_OK)

# backend/curation/views.py (add to existing) Define this next

class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny] # Only admin can see all raw articles
    # For debugging during development, you might set this to permissions.IsAuthenticated,
    # but revert for production if not intended for end users.

class UserNewsletterListView(generics.ListAPIView):
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show newsletters for the logged-in user
        return Newsletter.objects.filter(user=self.request.user).order_by('-generation_date')