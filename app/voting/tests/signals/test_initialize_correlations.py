from django.test import TestCase

from voting.factories import BallotOptionFactory, BallotFactory
from voting.models import OptionCorrelation


class InitializeCorrelationsTests(TestCase):
    def test__create_option__creates_expected_correlations(self):
        ballot = BallotFactory.create()
        BallotOptionFactory.create(ballot=ballot)
        BallotOptionFactory.create(ballot=ballot)

        self.assertEqual(OptionCorrelation.objects.all().count(), 4)

    def test__create_option__creates_option_as_target(self):
        ballot = BallotFactory.create()
        first = BallotOptionFactory.create(ballot=ballot)
        second = BallotOptionFactory.create(ballot=ballot)

        self.assertEqual(OptionCorrelation.objects.filter(
            predicate=first,
            target=second
        ).count(), 2)

    def test__create_option__creates_option_as_predicate(self):
        ballot = BallotFactory.create()
        first = BallotOptionFactory.create(ballot=ballot)
        second = BallotOptionFactory.create(ballot=ballot)

        self.assertEqual(OptionCorrelation.objects.filter(
            predicate=second,
            target=first
        ).count(), 2)
