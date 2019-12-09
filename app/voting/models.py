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
    ballot = models.ForeignKey(Ballot,
                               on_delete=models.CASCADE)
    label = models.CharField(max_length=255)

    class Meta:
        unique_together = [['ballot', 'label']]


class VotingSession(ChangeTrackModel):
    ballot = models.ForeignKey(Ballot,
                               on_delete=models.CASCADE)


class UserVote(ChangeTrackModel):
    session = models.ForeignKey(VotingSession,
                                on_delete=models.CASCADE)
    option = models.ForeignKey(BallotOption,
                               on_delete=models.CASCADE)
    polarity = models.BooleanField()

    class Meta:
        unique_together = [['session', 'option']]
