from rest_framework.serializers import ValidationError


def get_voting_session_token(request):
    token = request.query_params.get('token')
    if token is None:
        raise ValidationError('Token is required')
    return token
