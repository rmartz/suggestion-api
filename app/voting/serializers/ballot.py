from voting.models import Ballot
from rest_framework import serializers


class BallotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ballot
        fields = ['label']

