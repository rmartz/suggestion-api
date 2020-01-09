from django.test import TestCase
from django.urls import reverse
from django.db.models.signals import post_save
from rest_framework import status
import factory

from voting.factories import (
    BallotOptionFactory,
    VotingSessionFactory,
    UserVoteFactory,
    OptionCorrelationFactory
)


class SuggestionListTests(TestCase):
    def test_suggestions__list_suggest_no_token__error(self):
        url = reverse('suggest-list')
        response = self.client.get(url + '?mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggestions__list_explore_no_token__error(self):
        url = reverse('suggest-list')
        response = self.client.get(url + '?mode=explore')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggestions__list_no_mode__error(self):
        session = VotingSessionFactory.create()

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggestions__list_invalid_mode__error(self):
        session = VotingSessionFactory.create()

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=invalid')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggestions__post__not_allowed(self):
        url = reverse('suggest-list')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_suggestions__delete__not_allowed(self):
        url = reverse('suggest-list')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_suggestions__put__not_allowed(self):
        url = reverse('suggest-list')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SuggestionLikelihoodTests(TestCase):
    def test_suggestions__list__includes_options(self):
        ballot_option = BallotOptionFactory.create()
        session = VotingSessionFactory.create(room__ballot=ballot_option.ballot)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 1)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], ballot_option.id)

    def test_suggestions__list__exclude_unrelated_options(self):
        UserVoteFactory.create()
        session = VotingSessionFactory.create()

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_suggestions__list__exclude_voted_options(self):
        ballot_option = BallotOptionFactory.create()
        user_vote = UserVoteFactory.create(option=ballot_option)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={user_vote.session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_suggestions__list__voted_for_ranks_higher(self):
        """Option that is voted for after other should be suggested first."""

        base_vote = UserVoteFactory.create(polarity=False)
        voted_for = UserVoteFactory.create(
            option__ballot=base_vote.option.ballot,
            session=base_vote.session,
            polarity=True
        )
        session = VotingSessionFactory(room__ballot=base_vote.option.ballot)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], voted_for.option.id)
        self.assertIn('id', json['results'][1])
        self.assertEqual(json['results'][1]['id'], base_vote.option.id)

    def test_suggestions__list__voted_against_ranks_lower(self):
        """Option that is voted against after other should be suggested last."""

        base_vote = UserVoteFactory.create(polarity=True)
        voted_against = UserVoteFactory.create(
            option__ballot=base_vote.option.ballot,
            session=base_vote.session,
            polarity=False
        )
        session = VotingSessionFactory(room__ballot=base_vote.option.ballot)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], base_vote.option.id)
        self.assertIn('id', json['results'][1])
        self.assertEqual(json['results'][1]['id'], voted_against.option.id)

    def test_suggestions__other_session_voted_against__excluded(self):
        # Do not suggest options another session in the same room voted against
        session = VotingSessionFactory.create()
        UserVoteFactory.create(
            session__room=session.room,
            polarity=False
        )

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 0)

    def test_suggestions__other_session_voted_for__included(self):
        # Suggest options that another room voted on if they voted for it
        session = VotingSessionFactory.create()
        vote = UserVoteFactory.create(
            session__room=session.room,
            polarity=True
        )

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 1)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], vote.option.id)


class SuggestionSignificanceTests(TestCase):
    @factory.django.mute_signals(post_save)
    def test_exploration__list__includes_options(self):
        predicate = BallotOptionFactory.create()
        target = BallotOptionFactory.create(ballot=predicate.ballot)
        session = VotingSessionFactory.create(room__ballot=predicate.ballot)

        # Create correlations that give predicate->target a 0.8 spread
        OptionCorrelationFactory.create(
            predicate=predicate,
            predicate_polarity=True,
            target=target,
            correlation=0.9
        )
        OptionCorrelationFactory.create(
            predicate=predicate,
            predicate_polarity=False,
            target=target,
            correlation=0.1
        )

        # Create correlations that give target->predicate a even 0.5 likelihood
        OptionCorrelationFactory.create(
            predicate=target,
            predicate_polarity=True,
            target=predicate,
            correlation=0.5
        )
        OptionCorrelationFactory.create(
            predicate=target,
            predicate_polarity=False,
            target=predicate,
            correlation=0.5
        )

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=explore')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], predicate.id)
        # The predicate option should have a score of 0.8, as it has a 0.8 spread
        # and a perfect 0.5 likelihood
        self.assertEqual(json['results'][0]['score'], 0.8)
        self.assertIn('id', json['results'][1])
        self.assertEqual(json['results'][1]['id'], target.id)
        # The target option should have a score of 0, as it has the same correlation with predicate
        # for both polarities
        self.assertEqual(json['results'][1]['score'], 0)

    @factory.django.mute_signals(post_save)
    def test_exploration__high_likelihood__decreases_score(self):
        predicate = BallotOptionFactory.create()
        target = BallotOptionFactory.create(ballot=predicate.ballot)
        session = VotingSessionFactory.create(room__ballot=predicate.ballot)

        # Create correlations that give predicate->target a 0.8 spread
        OptionCorrelationFactory.create(
            predicate=predicate,
            predicate_polarity=True,
            target=target,
            correlation=0.9
        )
        OptionCorrelationFactory.create(
            predicate=predicate,
            predicate_polarity=False,
            target=target,
            correlation=0.1
        )

        # Create correlations that give target->predicate a even 0.5 likelihood
        OptionCorrelationFactory.create(
            predicate=target,
            predicate_polarity=True,
            target=predicate,
            correlation=0.9
        )
        OptionCorrelationFactory.create(
            predicate=target,
            predicate_polarity=False,
            target=predicate,
            correlation=0.9
        )

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=explore')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], predicate.id)
        # The predicate option should have a score above 0 and below 0.8, as it has a 0.8 spread
        # but a 0.9 likelihood (Which decreases the score)
        self.assertLess(json['results'][0]['score'], 0.8)
        self.assertGreater(json['results'][0]['score'], 0)

    @factory.django.mute_signals(post_save)
    def test_exploration__low_likelihood__decreases_score(self):
        predicate = BallotOptionFactory.create()
        target = BallotOptionFactory.create(ballot=predicate.ballot)
        session = VotingSessionFactory.create(room__ballot=predicate.ballot)

        # Create correlations that give predicate->target a 0.8 spread
        OptionCorrelationFactory.create(
            predicate=predicate,
            predicate_polarity=True,
            target=target,
            correlation=0.9
        )
        OptionCorrelationFactory.create(
            predicate=predicate,
            predicate_polarity=False,
            target=target,
            correlation=0.1
        )

        # Create correlations that give target->predicate a even 0.5 likelihood
        OptionCorrelationFactory.create(
            predicate=target,
            predicate_polarity=True,
            target=predicate,
            correlation=0.1
        )
        OptionCorrelationFactory.create(
            predicate=target,
            predicate_polarity=False,
            target=predicate,
            correlation=0.1
        )

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}&mode=explore')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], predicate.id)
        # The predicate option should have a score above 0 and below 0.8, as it has a 0.8 spread
        # but a 0.1 likelihood (Which decreases the score)
        self.assertLess(json['results'][0]['score'], 0.8)
        self.assertGreater(json['results'][0]['score'], 0)
