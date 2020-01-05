from itertools import permutations

from django.db.models.signals import post_save
from django.db.models import F
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
    # Use exponential moving average to adjust correlation weights
    # Correlation will vary between -1 and 1
    # Values towards 0 indicate a lack of correlation
    EMA_WEIGHT = 0.95

    score = 1 if instance.polarity else -1

    OptionCorrelation.objects.for_voting_session(
        instance.session
    ).filter(
        target=instance.option
    ).update(
        correlation=(F('correlation') * EMA_WEIGHT) + (score * (1 - EMA_WEIGHT))
    )
