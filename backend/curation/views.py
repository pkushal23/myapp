# backend/curation/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Interest, UserInterest
from .serializers import InterestSerializer, UserInterestSerializer, UserInterestsUpdateSerializer

class InterestListView(generics.ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow anyone to see available interests

class UserInterestView(generics.ListAPIView):
    serializer_class = UserInterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserInterest.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = UserInterestsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_interests_ids = serializer.validated_data.get('add_interests', [])
        remove_interests_ids = serializer.validated_data.get('remove_interests', [])

        user = request.user
        added_count = 0
        removed_count = 0

        with transaction.atomic():
            # Add interests
            for interest_id in add_interests_ids:
                try:
                    interest = Interest.objects.get(id=interest_id)
                    user_interest, created = UserInterest.objects.get_or_create(user=user, interest=interest)
                    if created:
                        added_count += 1
                except Interest.DoesNotExist:
                    return Response({"error": f"Interest with ID {interest_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Remove interests
            for interest_id in remove_interests_ids:
                try:
                    interest = Interest.objects.get(id=interest_id)
                    deleted_count, _ = UserInterest.objects.filter(user=user, interest=interest).delete()
                    removed_count += deleted_count
                except Interest.DoesNotExist:
                    return Response({"error": f"Interest with ID {interest_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": f"Successfully added {added_count} interests and removed {removed_count} interests.",
            "current_interests": UserInterestSerializer(self.get_queryset(), many=True).data
        }, status=status.HTTP_200_OK)
