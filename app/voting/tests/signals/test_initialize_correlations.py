from django.test import TestCase

from voting.factories import BallotOptionFactory, BallotFactory
from voting.models import OptionCorrelation


class InitializeCorrelationsTests(TestCase):
    def test__create_option__creates_correlation(self):
        ballot = BallotFactory.create()
        first = BallotOptionFactory.create(ballot=ballot)
        second = BallotOptionFactory.create(ballot=ballot)

        self.assertEqual(OptionCorrelation.objects.all().count(), 4)
        self.assertEqual(OptionCorrelation.objects.filter(
            predicate=first,
            target=second
        ).count(), 2)
        self.assertEqual(OptionCorrelation.objects.filter(
            predicate=second,
            target=first
        ).count(), 2)
