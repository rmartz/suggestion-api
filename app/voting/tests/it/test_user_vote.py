from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from voting.factories import UserVoteFactory, BallotOptionFactory, VotingSessionFactory
from voting.models import UserVote, OptionCorrelation


class UserVoteListTests(TestCase):
    def test_user_vote__list_no_token__error(self):
        url = reverse('uservote-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_vote__list_with_token__success(self):
        user_vote = UserVoteFactory.create()

        url = reverse('uservote-list')
        response = self.client.get(url + f'?token={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [{
            'id': user_vote.id,
            'option': user_vote.option.id,
            'polarity': user_vote.polarity
        }])

    def test_user_vote__list_other_token__missing(self):
        user_vote = UserVoteFactory.create()
        invalid_session = VotingSessionFactory(room=user_vote.session.room)

        url = reverse('uservote-list')
        response = self.client.get(url + f'?token={invalid_session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn('results', json)
        self.assertEqual(json['results'], [])


class UserVoteGetTests(TestCase):
    def test_user_vote__get_no_token__error(self):
        user_vote = UserVoteFactory.create()

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_vote__get_with_token__success(self):
        user_vote = UserVoteFactory.create()

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.get(url + f'?token={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'id': user_vote.id,
            'option': user_vote.option.id,
            'polarity': user_vote.polarity
        })

    def test_user_vote__get_invalid_token__error(self):
        user_vote = UserVoteFactory.create()
        invalid_session = VotingSessionFactory(room=user_vote.session.room)

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.get(url + f'?token={invalid_session.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserVoteCreateTests(TestCase):
    def test_user_vote__create_no_token__error(self):
        option = BallotOptionFactory.create()
        url = reverse('uservote-list')
        response = self.client.post(url, {
            'option': option.id,
            'polarity': True
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_vote__create_with_token__success(self):
        option = BallotOptionFactory.create()
        session = VotingSessionFactory.create(room__ballot=option.ballot)

        url = reverse('uservote-list')
        response = self.client.post(url + f'?token={session.id}', {
            'option': option.id,
            'polarity': True
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_vote__create_token_wrong_room__missing(self):
        option = BallotOptionFactory.create()
        invalid_session = VotingSessionFactory()

        url = reverse('uservote-list')
        response = self.client.post(url + f'?token={invalid_session.id}', {
            'option': option.id,
            'polarity': True
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserVoteUpdateTests(TestCase):
    def test_user_vote__update_no_token__error(self):
        user_vote = UserVoteFactory.create()

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.patch(url, {
            'polarity': not user_vote.polarity
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_vote__update_with_token__success(self):
        user_vote = UserVoteFactory.create()
        test_polarity = not user_vote.polarity

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.patch(url + f'?token={user_vote.session.id}', {
            'polarity': test_polarity
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_vote = UserVote.objects.get(id=user_vote.id)
        self.assertEqual(updated_vote.polarity, test_polarity)

    def test_user_vote__update_change_option__error(self):
        user_vote = UserVoteFactory.create()
        test_option = BallotOptionFactory(ballot=user_vote.option.ballot)

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.patch(url + f'?token={user_vote.session.id}', {
            'option': test_option.id
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_vote__update_invalid_token__error(self):
        user_vote = UserVoteFactory.create()
        invalid_session = VotingSessionFactory(room=user_vote.session.room)

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.patch(url + f'?token={invalid_session.id}', {
            'polarity': not user_vote.polarity
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_vote__update__no_double_vote(self):
        user_vote = UserVoteFactory.create(
            polarity=True
        )
        predicate = UserVoteFactory.create(session=user_vote.session)

        # Record what the correlation was at start
        initial_correlation = OptionCorrelation.objects.get(
            predicate=predicate.option,
            predicate_polarity=predicate.polarity,
            target=user_vote.option
        ).correlation

        # "Update" the vote to the same polarity it already had
        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        self.client.patch(url + f'?token={user_vote.session.id}', {
            'polarity': user_vote.polarity
        }, content_type='application/json')

        # The correlation score should not have increased further
        self.assertEqual(
            OptionCorrelation.objects.get(
                predicate=predicate.option,
                predicate_polarity=predicate.polarity,
                target=user_vote.option
            ).correlation,
            initial_correlation
        )


class UserVoteDeleteTests(TestCase):
    def test_user_vote__delete_no_token__error(self):
        user_vote = UserVoteFactory.create()

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_user_vote__delete_with_token__success(self):
        user_vote = UserVoteFactory.create()

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.delete(url + f'?token={user_vote.session.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserVote.objects.filter(id=user_vote.id).exists())

    def test_user_vote__delete_invalid_token__error(self):
        user_vote = UserVoteFactory.create()
        invalid_session = VotingSessionFactory(room=user_vote.session.room)

        url = reverse('uservote-detail', kwargs={'pk': user_vote.id})
        response = self.client.delete(url + f'?token={invalid_session.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
