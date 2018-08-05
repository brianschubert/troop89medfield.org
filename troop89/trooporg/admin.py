from django.contrib import admin

from .models import Patrol, ScoutMembership, Term


class PatrolMembershipInline(admin.TabularInline):
    model = Patrol.members.through
    extra = 0


@admin.register(ScoutMembership)
class ScoutMembershipAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)

    list_display = ('nickname', 'start', 'end')

    date_hierarchy = 'start'


@admin.register(Patrol)
class PatrolAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)

    list_display = ('name', 'date_created', 'is_active')
