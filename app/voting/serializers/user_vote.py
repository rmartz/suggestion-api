from rest_framework import serializers

from voting.models import UserVote


class UserVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVote
        fields = ['id', 'option', 'polarity', 'session']
        # read_only_fields = ['option']
        extra_kwargs = {
            'session': {'write_only': True}
        }

    def validate(self, data):
        try:
            if data['option'].ballot != data['session'].room.ballot:
                raise serializers.ValidationError('Option not valid for token')
        except KeyError:
            pass
        return data
