from voting.models import VotingSession
from rest_framework import serializers


class VotingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotingSession
        fields = ['ballot']

