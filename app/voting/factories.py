import factory
from .models import Ballot, BallotOption, Room, VotingSession, UserVote


class BallotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ballot

    @factory.sequence
    def label(n):
        return f'Test Ballot {n}'


class BallotOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BallotOption

    @factory.sequence
    def label(n):
        return f'Test Ballot Option {n}'

    ballot = factory.SubFactory(BallotFactory)


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    ballot = factory.SubFactory(BallotFactory)


class VotingSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VotingSession

    room = factory.SubFactory(RoomFactory)


class UserVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserVote

    session = factory.SubFactory(VotingSessionFactory)
    option = factory.SubFactory(
        BallotOptionFactory,
        ballot=factory.SelfAttribute('..session.room.ballot')
    )
    polarity = False
