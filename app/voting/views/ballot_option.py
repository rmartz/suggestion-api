from voting.models import BallotOption
from voting.serializers import BallotOptionSerializer
from rest_framework import viewsets


class BallotOptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BallotOption.objects.all().order_by('-created')
    serializer_class = BallotOptionSerializer

    def get_queryset(self):
        token = self.request.query_params.get('suggest-for')
        if token is not None:
            return self.suggest_for_session(token)

        return self.queryset

    def suggest_for_session(self, session_token):
        queryset = self.queryset.filter(
            # Get all options that are in the ballot for this session
            ballot__room__votingsession__id=session_token
        ).exclude(
            # But exclude any options that have already been voted
            uservote__session__id=session_token
        )

        return queryset
