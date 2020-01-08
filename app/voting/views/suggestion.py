from django.db.models import Q, F, Avg, OuterRef, Subquery, FloatField
from django.db.models.functions import Abs
from rest_framework import viewsets
from rest_framework.serializers import ValidationError

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
            score=self.get_score_annotation(session_token)
        ).values(
            'id',
            'score'
        ).order_by('-score')

    def get_score_annotation(self, session_token):
        mode = self.request.query_params.get('mode')
        try:
            func = {
                'suggest': self.get_likelihood_annotation,
                'explore': self.get_significance_annotation
            }[mode]
        except KeyError:
            raise ValidationError("param 'mode' must be either 'suggest' or 'explore'")
        else:
            return func(session_token)

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

        # We want to weigh the raw significance score by the likelihood of the option being chosen.
        # This centers around 0.5, so that a likelihood of 0.5 is a 1x multiplier, and drops off to
        #  0x for 100% or 0% likelihood.
        # This way, options that may have high impact but are unlikely to provide information about
        #  the user will be ranked below options that have a more moderate impact, but are more
        # likely to reveal something about the user's preferences.
        likelihood_score = (1 - 2 * Abs(
            0.5 - self.get_likelihood_annotation(session_token)))

        # Build a subquery of all correlations for relevant options
        # Since we want the difference, start getting all with polarity=True
        correlation_change = Subquery(OptionCorrelation.objects.filter(
            predicate=OuterRef('pk'),
            predicate_polarity=True
        ).annotate(
            # Next, annotate a new column called correlation_false for the same options,
            # but with polarity=False
            correlation_false=Subquery(
                OptionCorrelation.objects.filter(
                    predicate=OuterRef('predicate'),
                    predicate_polarity=False,
                    target=OuterRef('target')
                ).values('correlation')
            )
        ).values(
            # Then collapse the rows to just the absolute difference up or down
            correlation_change=Abs(
                F('correlation')-F('correlation_false')
            )
        ), output_field=FloatField())
        # Finally, average the absolute differences for all targets of a given predicate
        return likelihood_score * Avg(
            correlation_change,
            filter=Q(
                # Exclude options that the session has voted on, either as the predicate or target,
                # since we want options that are likely to affect future votes
                ~Q(
                    correlation_predicate__predicate__uservote__session=session_token) &
                ~Q(
                    correlation_predicate__target__uservote__session=session_token
                )
            )
        )
