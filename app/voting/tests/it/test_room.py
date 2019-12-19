from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import RoomFactory, BallotFactory
from voting.models import Room, Ballot, VotingSession


class RoomTests(TestCase):
    def test_room__list__success(self):
        room = RoomFactory.create()

        url = reverse('room-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [{
            'id': room.id,
            'ballot': room.ballot.id
        }])

    def test_room__get__success(self):
        room = RoomFactory.create()

        url = reverse('room-detail', kwargs={'pk': room.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'id': room.id,
            'ballot': room.ballot.id
        })

    def test_room__create__success(self):
        ballot = BallotFactory.create()
        url = reverse('room-list')
        response = self.client.post(url, {'ballot': ballot.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn('id', data)
        vs = Room.objects.get(id=data['id'])
        self.assertEqual(vs.ballot, ballot)

    def test_room__update__prohibited(self):
        room = RoomFactory.create()
        new_ballot = BallotFactory.create()

        url = reverse('room-detail', kwargs={'pk': room.id})
        response = self.client.patch(url, {'ballot': new_ballot.id},
                                     content_type='application/json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_room__delete__prohibited(self):
        room = RoomFactory.create()

        url = reverse('room-detail', kwargs={'pk': room.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class VotingSessionTests(TransactionTestCase):
    def tearDown(self):
        # These tests cannot be run in a transaction, as that prevents
        # Postgres's IntegrityError from being noticed inside the request
        # and instead happens when the transaction closes after the test.
        # So, we have to be sure to clean up the DB between tests manually:
        Ballot.objects.all().delete()

    def test_join__valid__success(self):
        room = RoomFactory.create()

        url = reverse('room-join', kwargs={'pk': room.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn('token', data)

        vs = VotingSession.objects.get(id=data['token'])
        self.assertEqual(vs.room, room)

    def test_join__invalid__prohibited(self):
        url = reverse('room-join', kwargs={'pk': 999})
        response = self.client.post(url)

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertQuerysetEqual(VotingSession.objects.all(), [])
