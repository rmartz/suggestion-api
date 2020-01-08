from rest_framework import serializers


class SuggestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    score = serializers.FloatField()
