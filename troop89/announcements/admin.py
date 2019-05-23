#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Announcement


@admin.register(Announcement)
class EventAdmin(MarkdownxModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_display = ('title', 'pub_date', 'author')

    fieldsets = (
        (None, {
            'fields': ('title', 'pub_date', 'content')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('author', 'slug')
        })
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        # Set the default author for new announcements to the current user
        form.base_fields['author'].initial = request.user
        return form

