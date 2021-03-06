from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import VotingSessionFactory, RoomFactory
from voting.models import VotingSession


class VotingSessionTests(TestCase):
    def test_voting_session__list__prohibited(self):
        url = reverse('votingsession-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_voting_session__get__success(self):
        voting_session = VotingSessionFactory.create()

        url = reverse('votingsession-detail', kwargs={'pk': voting_session.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'id': voting_session.id,
            'room': voting_session.room.id
        })

    def test_voting_session__create__success(self):
        room = RoomFactory.create()
        url = reverse('votingsession-list')
        response = self.client.post(url, {'room': room.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn('id', data)
        vs = VotingSession.objects.get(id=data['id'])
        self.assertEqual(vs.room, room)

    def test_voting_session__create_invalid_ballot__error(self):
        url = reverse('votingsession-list')
        response = self.client.post(url, {'room': 999})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_voting_session__update__prohibited(self):
        voting_session = VotingSessionFactory.create()
        new_room = RoomFactory.create()

        url = reverse('votingsession-detail', kwargs={'pk': voting_session.id})
        response = self.client.patch(url, {'room': new_room.id},
                                     content_type='application/json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_voting_session__delete__prohibited(self):
        voting_session = VotingSessionFactory.create()

        url = reverse('votingsession-detail', kwargs={'pk': voting_session.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
