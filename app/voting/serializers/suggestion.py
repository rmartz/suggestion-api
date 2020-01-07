from rest_framework import serializers


class SuggestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    likelihood = serializers.FloatField()
    significance = serializers.FloatField()
