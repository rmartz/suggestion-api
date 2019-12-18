from voting.models import Room
from voting.serializers import RoomSerializer
from rest_framework import viewsets, mixins


class RoomViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Room.objects.all().order_by('-created')
    serializer_class = RoomSerializer
