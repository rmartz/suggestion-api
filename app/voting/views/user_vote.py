from rest_framework import viewsets
from rest_framework.serializers import ValidationError

from voting.models import UserVote
from voting.serializers import UserVoteSerializer


class UserVoteViewSet(viewsets.ModelViewSet):
    queryset = UserVote.objects.all().order_by('-created')
    serializer_class = UserVoteSerializer

    def get_voting_session_token(self):
        token = self.request.query_params.get('token')
        if token is None:
            raise ValidationError('Token is required')
        return token

    def get_queryset(self):
        return self.queryset.filter(
            session=self.get_voting_session_token()
        )

    def create(self, request, *args, **kwargs):
        self.request.data['session'] = self.get_voting_session_token()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            del self.request.data['session']
        except KeyError:
            pass

        if 'option' in self.request.data:
            raise ValidationError('Option is read-only')

        return super().update(request, *args, **kwargs)
