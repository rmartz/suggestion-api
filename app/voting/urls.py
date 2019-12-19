from rest_framework import routers
from .views import (
    BallotViewSet,
    BallotOptionViewSet,
    RoomViewSet,
    VotingSessionViewSet
)

router = routers.DefaultRouter()
router.register(r'ballot', BallotViewSet)
router.register(r'ballotoption', BallotOptionViewSet)
router.register(r'room', RoomViewSet)
router.register(r'session', VotingSessionViewSet)
