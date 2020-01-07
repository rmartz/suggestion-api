from itertools import permutations

from django.db.models.signals import post_save
from django.db.models import F, Q, When, Case, OuterRef, Subquery, FloatField
from django.dispatch import receiver

from .models import UserVote, BallotOption, OptionCorrelation


@receiver(
    post_save,
    sender=BallotOption,
    dispatch_uid='initialize_correlations'
)
def initialize_correlations(sender, created, instance, **kwargs):
    if not created:
        return

    def generate_correlation_instances(existing_options, new_option):
        # Create a correlation between the new item and all existing options
        for existing_option in existing_options:
            # Create a correlation in both directions: existing->new and new->existing
            for predicate, target in permutations([existing_option, new_option]):
                # Create a correlation for when the predicate was chosen and when not
                for polarity in [True, False]:
                    yield OptionCorrelation(
                        predicate=predicate,
                        predicate_polarity=polarity,
                        target=target
                    )

    existing_options = BallotOption.objects.filter(
        ballot=instance.ballot,
        created__lt=instance.created
    )

    new_model_instances = generate_correlation_instances(existing_options, instance)

    OptionCorrelation.objects.bulk_create(new_model_instances)


@receiver(
    post_save,
    sender=UserVote,
    dispatch_uid='update_correlations'
)
def update_correlations(sender, instance, **kwargs):
    # Use Exponential Moving Average to track correlation weights
    # EMA will keep values stable, but allow them to drift in response to changes in patterns.
    # Higher the weight, the slower it will react to changes.
    # Correlation will vary between 0 and 1
    # Values towards 0.5 indicate a lack of correlation
    EMA_WEIGHT = 0.95
    POSITIVE_SCORE = 1
    NEGATIVE_SCORE = 0

    # Since we want to update all correlations for options this session has voted on, we expect to
    # update options where the target has already been voted on in the post.
    # This means we can't rely on `target.polarity` to get a score, and must read it from the
    # corresponding option's UserVote record
    match_score = Subquery(UserVote.objects.filter(
        session=instance.session,
        option=OuterRef('target_id')
    ).values(
        score=Case(
            When(polarity=True, then=POSITIVE_SCORE),
            default=NEGATIVE_SCORE,
            output_field=FloatField()
        )
    )[:1])

    OptionCorrelation.objects.filter(
        # Look for a predicate in a uservote in this session with the same polarity
        predicate__uservote__session=instance.session,
        predicate__uservote__polarity=F('predicate_polarity')
    ).filter(
        # ...and a target in this session as well
        target__uservote__session=instance.session,
    ).filter(
        # Check that the field we're triggered on is either a predicate or target
        # (To ensure we don't double-update the same vote)
        Q(target=instance.option) | Q(predicate=instance.option)
    ).update(
        # Use Exponential Moving Average to tweak the correlation
        correlation=(F('correlation') * EMA_WEIGHT) + (match_score * (1 - EMA_WEIGHT))
    )
