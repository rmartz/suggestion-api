from django.contrib import admin

from .models import Ballot, BallotOption


class BallotAdmin(admin.ModelAdmin):
    pass


class BallotOptionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ballot, BallotAdmin)
admin.site.register(BallotOption, BallotOptionAdmin)
