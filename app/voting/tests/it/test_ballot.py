from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import BallotFactory


class BallotTests(TestCase):
    def test_ballot__list__success(self):
        ballot = BallotFactory.create()

        url = reverse('ballot-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [{
            'id': ballot.id,
            'label': ballot.label
        }])

    def test_ballot__get__success(self):
        ballot = BallotFactory.create()

        url = reverse('ballot-detail', kwargs={'pk': ballot.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'id': ballot.id,
            'label': ballot.label
        })

    def test_ballot__create__prohibited(self):
        test_label = 'Test ballot'
        url = reverse('ballot-list')
        response = self.client.post(url, {'label': test_label})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_ballot__update__prohibited(self):
        ballot = BallotFactory.create()

        test_label = 'Test ballot'
        url = reverse('ballot-detail', kwargs={'pk': ballot.id})
        response = self.client.patch(url, {'label': test_label})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_ballot__delete__prohibited(self):
        ballot = BallotFactory.create()

        url = reverse('ballot-detail', kwargs={'pk': ballot.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
