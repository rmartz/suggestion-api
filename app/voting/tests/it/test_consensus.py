from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import BallotOptionFactory, VotingSessionFactory, UserVoteFactory


class ConsensusTests(TestCase):
    def test_consensus__create__prohibited(self):
        url = reverse('consensus-list')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_consensus__delete__prohibited(self):
        option = BallotOptionFactory.create()
        url = reverse('consensus-detail', kwargs={'pk': option.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_consensus__update__prohibited(self):
        option = BallotOptionFactory.create()
        url = reverse('consensus-detail', kwargs={'pk': option.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_consensus__list_no_token__error(self):
        url = reverse('consensus-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_consensus__list_with_token__success(self):
        session = VotingSessionFactory.create()
        url = reverse('consensus-list')
        response = self.client.get(url + f'?token={session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_consensus__voted_for__shows(self):
        vote = UserVoteFactory.create(polarity=True)
        url = reverse('consensus-list')
        response = self.client.get(url + f'?token={vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [{
            'id': vote.option.id
        }])

    def test_consensus__voted_against__excluded(self):
        vote = UserVoteFactory.create(polarity=False)
        url = reverse('consensus-list')
        response = self.client.get(url + f'?token={vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_consensus__vote_missing__excluded(self):
        # Exclude options that were voted for by one session but are missing a vote by another
        vote = UserVoteFactory.create(polarity=True)
        VotingSessionFactory.create(room=vote.session.room)
        url = reverse('consensus-list')
        response = self.client.get(url + f'?token={vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])
