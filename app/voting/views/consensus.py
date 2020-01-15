from django.db.models import Exists, OuterRef
from rest_framework import viewsets

from voting.models import BallotOption, VotingSession
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
        ).annotate(
            # A option is a consensus choice if there are no sessions that have not voted for it
            consensus=~Exists(
                VotingSession.objects.filter(
                    room__votingsession=session_token,
                ).exclude(
                    # Exclude any sessions that have a vote for this option
                    uservote__option_id=OuterRef('pk'),
                    uservote__polarity=True
                )
            )
        ).filter(
            consensus=True
        ).values('id')
