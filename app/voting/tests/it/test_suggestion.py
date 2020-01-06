from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import BallotOptionFactory, VotingSessionFactory, UserVoteFactory


class BallotOptionSuggestTests(TestCase):
    def test_suggestions__get__includes_options(self):
        ballot_option = BallotOptionFactory.create()
        session = VotingSessionFactory.create(room__ballot=ballot_option.ballot)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 1)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], ballot_option.id)

    def test_suggestions__get__exclude_unrelated_options(self):
        BallotOptionFactory.create()
        user_vote = UserVoteFactory.create()

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_suggestions__get__exclude_voted_options(self):
        ballot_option = BallotOptionFactory.create()
        user_vote = UserVoteFactory.create(option=ballot_option)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_suggestions__get__voted_for_ranks_higher(self):
        """Option that is voted for should be suggested before base option."""

        base_option = BallotOptionFactory.create()
        voted_for = UserVoteFactory.create(
            option__ballot=base_option.ballot,
            polarity=True
        )
        session = VotingSessionFactory(room__ballot=base_option.ballot)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        raise Exception(json)
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], voted_for.option.id)
        self.assertIn('id', json['results'][1])
        self.assertEqual(json['results'][1]['id'], base_option.id)

    def test_suggestions__get__voted_against_ranks_higher(self):
        """Option that is voted against should be suggested after base option."""

        base_option = BallotOptionFactory.create()
        voted_against = UserVoteFactory.create(
            option__ballot=base_option.ballot,
            polarity=False
        )
        session = VotingSessionFactory(room__ballot=base_option.ballot)

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(len(json['results']), 2)
        self.assertIn('id', json['results'][0])
        self.assertEqual(json['results'][0]['id'], base_option.id)
        self.assertIn('id', json['results'][1])
        self.assertEqual(json['results'][1]['id'], voted_against.option.id)
