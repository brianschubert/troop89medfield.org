from django.contrib import admin

from .models import Patrol, ScoutMembership


class PatrolMembershipInline(admin.TabularInline):
    model = Patrol.members.through
    extra = 0


@admin.register(ScoutMembership)
class ScoutMembershipAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)


@admin.register(Patrol)
class PatrolAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)

    list_display = ('name', 'date_created', 'is_active')

