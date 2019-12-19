from django.db import IntegrityError

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from voting.models import Room, VotingSession
from voting.serializers import RoomSerializer


class RoomViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Room.objects.all().order_by('-created')
    serializer_class = RoomSerializer

    @action(methods=['POST'], detail=True)
    def join(self, request, pk=None):
        try:
            session = VotingSession.objects.create(room_id=pk)
        except IntegrityError:
            return Response({
                'error': 'Invalid room ID'
            }, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'token': session.id
            }, status.HTTP_201_CREATED)
