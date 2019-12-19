from rest_framework import viewsets, mixins

from voting.models import Room
from voting.serializers import RoomSerializer


class RoomViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
        ):
    queryset = Room.objects.all().order_by('-created')
    serializer_class = RoomSerializer
