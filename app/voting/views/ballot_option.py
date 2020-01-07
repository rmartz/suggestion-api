from rest_framework import viewsets

from voting.models import BallotOption
from voting.serializers import BallotOptionSerializer


class BallotOptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BallotOption.objects.all().order_by('-created')
    serializer_class = BallotOptionSerializer
