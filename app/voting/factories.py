import factory
from .models import Ballot, BallotOption, VotingSession, UserVote


class BallotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ballot

    label = 'Test Ballot'


class BallotOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BallotOption

    label = 'Test Ballot Option'
    ballot = factory.SubFactory(BallotFactory)


class VotingSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VotingSession

    ballot = factory.SubFactory(BallotFactory)


class UserVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserVote

    session = factory.SubFactory(VotingSessionFactory)
    option = factory.SubFactory(
        BallotOptionFactory,
        ballot=factory.SelfAttribute('session.ballot')
    )
    polarity = False
