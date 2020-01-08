from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import BallotOptionFactory, VotingSessionFactory, UserVoteFactory


class SuggestionListTests(TestCase):
    def test_suggestions__list_no_token__error(self):
        url = reverse('suggest-list')
        response = self.client.get(url + '?mode=suggest')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggestions__list_no_mode__error(self):
        session = VotingSessionFactory.create()

        url = reverse('suggest-list')
        response = self.client.get(url + f'?token={session.id}')

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
