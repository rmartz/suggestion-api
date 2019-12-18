from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import RoomFactory, BallotFactory
from voting.models import Room


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
