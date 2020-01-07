from django.db.models import Q, F, Avg, OuterRef, Subquery
from django.db.models.functions import Abs
from rest_framework import viewsets

from voting.models import BallotOption, OptionCorrelation
from voting.serializers import SuggestionSerializer
from .utils import get_voting_session_token


class SuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OptionCorrelation.objects.all().order_by('-created')
    serializer_class = SuggestionSerializer

    def get_queryset(self):
        session_token = get_voting_session_token(self.request)

        return BallotOption.objects.filter(
            ballot__room__votingsession=session_token
        ).exclude(
            # Do not offer suggestions that have already been voted on
            uservote__session=session_token
        ).annotate(
            likelihood=self.get_likelihood_annotation(session_token),
            significance=self.get_likelihood_annotation(session_token),
        ).values(
            'id',
            'likelihood',
            'significance'
        ).order_by('-likelihood')

    def get_likelihood_annotation(self, session_token):
        # Average the correlation value over all rows for predicates this session has not excluded
        # (i.e., either has not voted on or has voted matching the row)
        return Avg(
            'correlation_target__correlation',
            filter=~Q(
                correlation_target__predicate__uservote__session=session_token
            ) | Q(
                correlation_target__predicate__uservote__session=session_token,
                correlation_target__predicate_polarity=F(
                    'correlation_target__predicate__uservote__polarity'
                )
            )
        )

    def get_significance_annotation(self, session_token):
        # Calculate the absolute difference in correlation of the two polarities for a given target.
        # Exclude any correlation that this session has voted for, either as predicate or target.
        # (Exclude already voted predicates as they cannot be suggestions, and already
        # voted targets as we want to maximize effect on future suggestions)
        # e.g., if A has a 0.3 correlation with B, and ~A has a 0.8 correlation with B, then A has
        # a significance of 0.5 with B
        correlation_change = OptionCorrelation.objects.filter(
            predicate=OuterRef('pk'),
            polarity=True
        ).annotate(
            correlation_false=Subquery(
                OptionCorrelation.objects.filter(
                    predicate=OuterRef('predicate'),
                    polarity=False,
                    target=OuterRef('target')
                ).values('correlation')
            )
        ).values(
            correlation_change=Abs(
                F('correlation')-F('correlation_false')
            )
        )
        return Avg(
            correlation_change,
            filter=Q(
                ~Q(
                    correlation_predicate__predicate__uservote__session=session_token) &
                ~Q(
                    correlation_predicate__target__uservote__session=session_token
                )
            )
        )
