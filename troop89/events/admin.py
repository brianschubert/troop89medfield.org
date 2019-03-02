#  Copyright (c) 2018, 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Event, EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(MarkdownxModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_display = ('title', 'type', 'start', 'end')

    list_filter = ('type', 'start')

    date_hierarchy = 'start'

    fieldsets = (
        (None, {
            'fields': ('title', 'type', 'description', 'start', 'end')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('slug',)
        })
    )
