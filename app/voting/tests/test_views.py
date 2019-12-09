from django.test import TestCase
from django.urls import reverse

from voting.models import Ballot


class MyTests(TestCase):
    def test_ballot_create__success(self):
        test_label = 'Test ballot'
        url = reverse('ballot-list')
        response = self.client.post(url, {'label': test_label})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ballot.objects.filter(label=test_label).count(), 1)
