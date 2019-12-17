from voting.models import VotingSession
from voting.serializers import VotingSessionSerializer
from rest_framework import viewsets, mixins


class VotingSessionViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = VotingSession.objects.all().order_by('-created')
    serializer_class = VotingSessionSerializer
