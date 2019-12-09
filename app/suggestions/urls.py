from django.urls import include, path
from django.contrib import admin
from rest_framework import routers

from voting.urls import router as voting_router

router = routers.DefaultRouter()
router.registry.extend(voting_router.registry)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework'))
]
