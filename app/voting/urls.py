from rest_framework import routers
from .views import BallotViewSet, BallotOptionViewSet, VotingSessionViewSet

router = routers.DefaultRouter()
router.register(r'ballot', BallotViewSet)
router.register(r'ballotoption', BallotOptionViewSet)
router.register(r'room', VotingSessionViewSet)
