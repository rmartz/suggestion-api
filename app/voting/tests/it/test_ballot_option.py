from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import BallotOptionFactory


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
