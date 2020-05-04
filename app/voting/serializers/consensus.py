from rest_framework import serializers


class ConsensusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
