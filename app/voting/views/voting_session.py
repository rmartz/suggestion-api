from rest_framework import viewsets, mixins

from voting.models import VotingSession
from voting.serializers import VotingSessionSerializer


class VotingSessionViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
        ):
    queryset = VotingSession.objects.all()
    serializer_class = VotingSessionSerializer
