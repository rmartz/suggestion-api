import factory
from .models import Ballot


class BallotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ballot

    label = 'Test Ballot'
