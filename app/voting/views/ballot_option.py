from voting.models import BallotOption
from voting.serializers import BallotOptionSerializer
from rest_framework import viewsets


class BallotOptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BallotOption.objects.all().order_by('-created')
    serializer_class = BallotOptionSerializer
