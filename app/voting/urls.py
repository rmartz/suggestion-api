from rest_framework import routers
from .views import BallotViewSet

router = routers.DefaultRouter()
router.register(r'ballot', BallotViewSet)
