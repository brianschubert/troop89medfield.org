#  Copyright (c) 2019 Brian Schubert
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from ckeditor.widgets import CKEditorWidget
from csp.decorators import csp_update
from django import forms
from django.contrib import admin
from django.contrib.flatpages import admin as flatpage_admin, forms as flatpage_forms
from django.contrib.flatpages.models import FlatPage
from django.utils import html
from django.utils.decorators import method_decorator
from django.utils.text import Truncator

from .models import HierarchicalFlatPage

# The CKEditorWidget requires inline css and javascript, which violate the
# site-wide CSP. This decorator loosens the CSP on the admin pages that load
# the editor widget.
_CSP_UPDATE_DECORATOR = csp_update(
    SCRIPT_SRC=("'unsafe-inline'", 'www.webspellchecker.net/spellcheck31/'),
    STYLE_SRC="'unsafe-inline'",
    IMG_SRC='data:',  # used by the iframe tools
    FRAME_SRC=( # used by ckeditor spell checker
        'https://svc.webspellchecker.net/spellcheck/lf/23/banner/banner.html',
        'www.webspellchecker.net/spellcheck/script/ssrv.cgi'
    ),
)


class ParentPageListFilter(admin.SimpleListFilter):
    title = "parent page"

    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        pages = HierarchicalFlatPage.objects.children_for_url('/', depth=3)
        return [(p.url, p.url) for p in pages]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(url__startswith=self.value())


class HierarchicalFlatPageAdminForm(flatpage_forms.FlatpageForm):
    content = forms.CharField(
        widget=CKEditorWidget(),
        help_text='Tip: use the "Source" button the view the pages HTML source.',
    )
    # Copy of FlatPageForm.url, but with overridden widget
    url = forms.RegexField(
        label="URL",
        max_length=100,
        regex=r'^[-\w/\.~]+$',
        help_text="Example: '/about/contact/'. Make sure to have leading and trailing slashes.",
        error_messages={
            "invalid":
                "This value must contain only letters, numbers, dots, "
                "underscores, dashes, slashes or tildes.",
        },
        widget=forms.TextInput(attrs={'size': 50}),
    )

    class Meta(flatpage_forms.FlatpageForm.Meta):
        model = HierarchicalFlatPage


@method_decorator(_CSP_UPDATE_DECORATOR, name='add_view')
@method_decorator(_CSP_UPDATE_DECORATOR, name='change_view')
class HierarchicalFlatPageAdmin(flatpage_admin.FlatPageAdmin):
    form = HierarchicalFlatPageAdminForm

    search_fields = ['title', 'url']

    list_display = flatpage_admin.FlatPageAdmin.list_display + ('content_preview',)

    list_display_links = ('url', 'title')

    list_filter = (ParentPageListFilter,)

    @staticmethod
    def content_preview(obj: HierarchicalFlatPage) -> str:
        content = html.strip_tags(obj.content)
        return Truncator(content).chars(90, html=True)


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(HierarchicalFlatPage, HierarchicalFlatPageAdmin)
