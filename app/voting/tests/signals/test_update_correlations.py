from django.test import TestCase

from voting.factories import UserVoteFactory, VotingSessionFactory, BallotFactory
from voting.models import OptionCorrelation


class UpdateCorrelationsTests(TestCase):
    def test__user_vote_positive_polarity__increases_correlation(self):
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session)
        second = UserVoteFactory.create(session=session, polarity=True)

        self.assertGreater(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=first.polarity,
                target=second.option
            ).correlation,
            0.5
        )

    def test__user_vote_negative_polarity__decreases_correlation(self):
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session)
        second = UserVoteFactory.create(session=session, polarity=False)

        self.assertLess(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=first.polarity,
                target=second.option
            ).correlation,
            0.5
        )

    def test__user_vote_wrong_polarity__no_effect(self):
        # A vote should not affect correlations for the other polarity
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session)
        second = UserVoteFactory.create(session=session)

        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=not first.polarity,
                target=second.option
            ).correlation,
            0.5
        )

    def test__user_vote_wrong_polarity__no_effect_inverse(self):
        # A vote should not affect correlations for the other polarity made before
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session)
        second = UserVoteFactory.create(session=session)

        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=second.option,
                predicate_polarity=not second.polarity,
                target=first.option
            ).correlation,
            0.5
        )

    def test__user_vote__affects_inverse(self):
        # Correlations targetting a vote made before should be affected by votes made after
        session = VotingSessionFactory.create()
        first = UserVoteFactory.create(session=session, polarity=False)
        second = UserVoteFactory.create(session=session)

        self.assertLess(
            OptionCorrelation.objects.get(
                predicate=second.option,
                predicate_polarity=second.polarity,
                target=first.option
            ).correlation,
            0.5
        )

    def test__different_session_user_vote__no_effect(self):
        # A vote made first should have no change with votes from another session made after
        ballot = BallotFactory.create()
        first = UserVoteFactory.create(session__room__ballot=ballot, polarity=False)
        second = UserVoteFactory.create(session__room__ballot=ballot)

        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=second.option,
                predicate_polarity=second.polarity,
                target=first.option
            ).correlation,
            0.5
        )

    def test__different_session_user_vote__no_effect_inverse(self):
        # A vote made after should have on correlation with votes from another session made before
        ballot = BallotFactory.create()
        first = UserVoteFactory.create(session__room__ballot=ballot)
        second = UserVoteFactory.create(session__room__ballot=ballot, polarity=False)

        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=first.option,
                predicate_polarity=first.polarity,
                target=second.option
            ).correlation,
            0.5
        )
