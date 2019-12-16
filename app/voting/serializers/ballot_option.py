from voting.models import BallotOption
from rest_framework import serializers


class BallotOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BallotOption
        fields = ['label', 'ballot']

