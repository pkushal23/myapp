# backend/curation/serializers.py
from rest_framework import serializers
from .models import Interest, UserInterest
from django.contrib.auth.models import User

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'

class UserInterestSerializer(serializers.ModelSerializer):
    interest_name = serializers.CharField(source='interest.name', read_only=True)
    interest_id = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(), source='interest', write_only=True
    )

    class Meta:
        model = UserInterest
        fields = ('id', 'user', 'interest', 'interest_name', 'interest_id')
        read_only_fields = ('user', 'interest') # 'user' is set by the view, 'interest' from 'interest_id'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure 'interest' field shows full object on read
        representation['interest'] = InterestSerializer(instance.interest).data
        return representation

class UserInterestsUpdateSerializer(serializers.Serializer):
    add_interests = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
    )
    remove_interests = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
    )