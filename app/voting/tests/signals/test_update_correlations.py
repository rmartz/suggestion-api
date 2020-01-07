from django.test import TestCase

from voting.factories import UserVoteFactory, VotingSessionFactory, BallotFactory
from voting.models import OptionCorrelation


class UpdateCorrelationsTests(TestCase):
    def test__user_vote_positive_polarity__increases_correlation(self):
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session, polarity=False)
        second = UserVoteFactory.create(session=session, polarity=True)

        self.assertGreater(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=False,
                target=second.option
            ).correlation,
            0.5
        )

    def test__user_vote_negative_polarity__decreases_correlation(self):
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session, polarity=False)
        second = UserVoteFactory.create(session=session, polarity=False)

        self.assertLess(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=False,
                target=second.option
            ).correlation,
            0.5
        )

    def test__user_vote__affects_inverse(self):
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session, polarity=False)
        second = UserVoteFactory.create(session=session, polarity=True)

        self.assertLess(
            OptionCorrelation.objects.get(
                predicate=second.option,
                predicate_polarity=True,
                target=first.option
            ).correlation,
            0.5
        )

    def test__different_session_user_vote__no_effect(self):
        ballot = BallotFactory.create()
        first = UserVoteFactory.create(session__room__ballot=ballot, polarity=False)
        second = UserVoteFactory.create(session__room__ballot=ballot, polarity=True)

        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=second.option,
                predicate_polarity=True,
                target=first.option
            ).correlation,
            0.5
        )

    def test__different_session_user_vote__no_effect_inverse(self):
        ballot = BallotFactory.create()
        first = UserVoteFactory.create(session__room__ballot=ballot, polarity=True)
        second = UserVoteFactory.create(session__room__ballot=ballot, polarity=False)

        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=True,
                target=second.option
            ).correlation,
            0.5
        )
