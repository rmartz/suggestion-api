from rest_framework import routers
from .views import (
    BallotViewSet,
    BallotOptionViewSet,
    RoomViewSet,
    VotingSessionViewSet,
    UserVoteViewSet,
    SuggestionViewSet,
    ConsensusViewSet
)

router = routers.DefaultRouter()
router.register(r'ballot', BallotViewSet)
router.register(r'ballotoption', BallotOptionViewSet)
router.register(r'room', RoomViewSet)
router.register(r'session', VotingSessionViewSet)
router.register(r'vote', UserVoteViewSet)
router.register(r'suggest', SuggestionViewSet, basename='suggest')
router.register(r'picks', ConsensusViewSet, basename='consensus')
