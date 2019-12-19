from voting.models import Ballot
from voting.serializers import BallotSerializer
from rest_framework import viewsets


class BallotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ballot.objects.all().order_by('-created')
    serializer_class = BallotSerializer
