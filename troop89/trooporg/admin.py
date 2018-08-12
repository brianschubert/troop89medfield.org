from django.contrib import admin

from .models import Member, Patrol, Term


class PatrolMembershipInline(admin.TabularInline):
    model = Patrol.members.through
    extra = 0


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    # Note: if editing user fields from the member admin is desired, simply
    # swap out the base class with the standard UserAdmin or derivative and
    # add the relevant fields/fieldsets.
    inlines = (PatrolMembershipInline,)

    fields = ('first_name', 'last_name')

    list_display = ('first_name', 'last_name', 'is_adult_view', 'is_active_member_view')

    list_display_links = ('first_name', 'last_name')

    def is_adult_view(self, obj: Member) -> bool:
        return obj.is_adult()

    is_adult_view.boolean = True

    is_adult_view.short_description = 'Adult'

    def is_active_member_view(self, obj: Member) -> bool:
        return obj.is_active_member()

    is_active_member_view.boolean = True

    is_active_member_view.short_description = 'Active Member'


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)

    list_display = ('nickname', 'start', 'end')

    date_hierarchy = 'start'

    empty_value_display = '(none)'


@admin.register(Patrol)
class PatrolAdmin(admin.ModelAdmin):
    inlines = (PatrolMembershipInline,)

    list_display = ('name', 'date_created', 'is_active')

    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {
            'fields': ('name', 'date_created')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('slug',)
        })
    )
