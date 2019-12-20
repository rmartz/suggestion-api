from rest_framework import viewsets
from rest_framework.serializers import ValidationError

from voting.models import UserVote
from voting.serializers import UserVoteSerializer


class UserVoteViewSet(viewsets.ModelViewSet):
    queryset = UserVote.objects.all().order_by('-created')
    serializer_class = UserVoteSerializer

    def get_queryset(self):
        queryset = self.queryset

        token = self.request.query_params.get('token')
        if token is None:
            raise ValidationError('Token is required')

        return queryset.filter(session=token)

    def create(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        if token is None:
            raise ValidationError('Token is required')

        self.request.data['session'] = token
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            del self.request.data['session']
        except KeyError:
            pass

        if 'option' in self.request.data:
            raise ValidationError('Option is read-only')

        return super().update(request, *args, **kwargs)
