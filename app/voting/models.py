from django.db import models


class ChangeTrackModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Ballot(ChangeTrackModel):
    label = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.label}"


class BallotOption(ChangeTrackModel):
    ballot = models.ForeignKey(
        Ballot,
        on_delete=models.CASCADE
    )
    label = models.CharField(max_length=255)

    class Meta:
        unique_together = [['ballot', 'label']]

    def __str__(self):
        return f"{self.ballot.label} - {self.label}"


class Room(ChangeTrackModel):
    ballot = models.ForeignKey(
        Ballot,
        on_delete=models.CASCADE
    )


class VotingSession(ChangeTrackModel):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )


class UserVote(ChangeTrackModel):
    session = models.ForeignKey(
        VotingSession,
        on_delete=models.CASCADE
    )
    option = models.ForeignKey(
        BallotOption,
        on_delete=models.CASCADE
    )
    polarity = models.BooleanField()

    class Meta:
        unique_together = [['session', 'option']]


class OptionCorrelation(ChangeTrackModel):
    predicate = models.ForeignKey(
        BallotOption,
        on_delete=models.CASCADE,
        related_name='correlation_predicate'
    )
    predicate_polarity = models.BooleanField()

    target = models.ForeignKey(
        BallotOption,
        on_delete=models.CASCADE,
        related_name='correlation_target'
    )

    correlation = models.FloatField(default=0.5)

    class Meta:
        unique_together = [['predicate', 'predicate_polarity', 'target']]
