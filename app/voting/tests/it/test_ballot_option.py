from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import BallotOptionFactory, VotingSessionFactory, UserVoteFactory


class BallotOptionListTests(TestCase):
    def test_ballot_option__list__success(self):
        ballot_option = BallotOptionFactory.create()

        url = reverse('ballotoption-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [{
            'id': ballot_option.id,
            'ballot': ballot_option.ballot.id,
            'label': ballot_option.label
        }])


class BallotOptionGetTests(TestCase):
    def test_ballot_option__get__success(self):
        ballot_option = BallotOptionFactory.create()

        url = reverse('ballotoption-detail', kwargs={'pk': ballot_option.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'id': ballot_option.id,
            'ballot': ballot_option.ballot.id,
            'label': ballot_option.label
        })


class BallotOptionCreateTests(TestCase):
    def test_ballot_option__create__prohibited(self):
        test_label = 'Test ballot option'
        url = reverse('ballotoption-list')
        response = self.client.post(url, {'label': test_label})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class BallotOptionUpdateTests(TestCase):
    def test_ballot_option__update__prohibited(self):
        ballot_option = BallotOptionFactory.create()

        test_label = 'Test ballot option'
        url = reverse('ballotoption-detail', kwargs={'pk': ballot_option.id})
        response = self.client.patch(url, {'label': test_label})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class BallotOptionDeleteTests(TestCase):
    def test_ballot_option__delete__prohibited(self):
        ballot_option = BallotOptionFactory.create()

        url = reverse('ballotoption-detail', kwargs={'pk': ballot_option.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class BallotOptionSuggestTests(TestCase):
    def test_suggestions__get__includes_options(self):
        ballot_option = BallotOptionFactory.create()
        session = VotingSessionFactory.create(room__ballot=ballot_option.ballot)

        url = reverse('ballotoption-list')
        response = self.client.get(url + f'?suggest-for={session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [{
            'ballot': ballot_option.ballot.id,
            'id': ballot_option.id,
            'label': ballot_option.label
        }])

    def test_suggestions__get__exclude_unrelated_options(self):
        BallotOptionFactory.create()
        user_vote = UserVoteFactory.create()

        url = reverse('ballotoption-list')
        response = self.client.get(url + f'?suggest-for={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])

    def test_suggestions__get__exclude_voted_options(self):
        ballot_option = BallotOptionFactory.create()
        user_vote = UserVoteFactory.create(option=ballot_option)

        url = reverse('ballotoption-list')
        response = self.client.get(url + f'?suggest-for={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])
