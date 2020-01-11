from django.contrib import admin

from .models import Ballot, BallotOption


class BallotAdmin(admin.ModelAdmin):
    pass


class BallotOptionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'ballot'
        )


admin.site.register(Ballot, BallotAdmin)
admin.site.register(BallotOption, BallotOptionAdmin)
