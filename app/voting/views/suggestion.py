from django.db.models import F, Avg, OuterRef, Subquery, FloatField
from django.db.models.functions import Abs
from rest_framework import viewsets
from rest_framework.serializers import ValidationError

from voting.models import BallotOption, OptionCorrelation
from voting.serializers import SuggestionSerializer
from .utils import get_voting_session_token


class SuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BallotOption.objects.all()
    serializer_class = SuggestionSerializer
    LIKELIHOOD = 'suggest'
    SIGNIFICANCE = 'explore'

    def get_queryset(self):
        session_token = get_voting_session_token(self.request)
        mode = self.request.query_params.get('mode')

        queryset = self.queryset.filter(
            ballot__room__votingsession=session_token
        ).exclude(
            # Do not offer suggestions that have already been voted on
            uservote__session=session_token
        ).annotate(
            score=self.get_score_annotation(mode, session_token)
        )

        if mode == self.LIKELIHOOD:
            # In likelihood mode, do not include suggestions that another session has voted against.
            # This isn't a problem in explore mode, since even if we know an option can't be a
            # consensus choice, suggesting it can provide us with information about the user
            queryset = queryset.exclude(
                uservote__polarity=False,
                uservote__session__room__votingsession=session_token
            )

        return queryset.values(
            'id',
            'score'
        ).order_by('-score')

    def get_score_annotation(self, mode, session_token):
        try:
            func = {
                self.LIKELIHOOD: self.get_likelihood_annotation,
                self.SIGNIFICANCE: self.get_significance_annotation
            }[mode]
        except KeyError:
            raise ValidationError(
               f"param 'mode' must be either '{self.LIKELIHOOD}' or '{self.SIGNIFICANCE}'")
        else:
            return func(session_token)

    def get_likelihood_annotation(self, session_token):
        # Average the correlation value over all rows for predicates this session has not excluded
        # That is either has not voted on or has voted matching the row
        # This is equivalent to there not being a vote for the wrong polarity

        likelihood_correlations = Subquery(
            OptionCorrelation.objects.filter(
                target=OuterRef('pk')
            ).exclude(
                predicate__uservote__session=session_token,
                predicate_polarity=not F(
                        'predicate__uservote__polarity'
                    )
            ).values('correlation')[:1],
            output_field=FloatField()
        )

        return Avg(likelihood_correlations)

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
        correlation_change = OptionCorrelation.objects.filter(
            predicate=OuterRef('pk'),
        ).exclude(
            # Exclude options that the session has voted on, either as the predicate or target,
            # since we want options that are likely to affect future votes
            target__uservote__session=session_token
        ).values(
            'correlation'
        )

        correlation_true = Subquery(correlation_change.filter(
            predicate_polarity=True
        )[:1], output_field=FloatField())

        correlation_false = Subquery(correlation_change.filter(
            predicate_polarity=False
        )[:1], output_field=FloatField())

        # Finally, average the absolute differences for all targets of a given predicate
        return likelihood_score * Avg(Abs(
            correlation_true - correlation_false
        ))
