from django.db.models import Count, Q
from rest_framework import viewsets

from voting.models import BallotOption
from voting.serializers import ConsensusSerializer
from .utils import get_voting_session_token


class ConsensusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BallotOption.objects.all().order_by('created')
    serializer_class = ConsensusSerializer

    def get_queryset(self):
        session_token = get_voting_session_token(self.request)

        return self.queryset.filter(
            # Only show options for the ballot that this session belongs to
            ballot__room__votingsession=session_token
        ).exclude(
            # Do not include options that have received any votes against in this room
            uservote__polarity=False,
            uservote__votingsession__room__votingsession=session_token
        ).annotate(
            count=Count(
                'uservote',
                filter=Q(uservote__votingsession__room__votingsession=session_token))
        ).values('id', 'count')
