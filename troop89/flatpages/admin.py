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
from django.utils.decorators import method_decorator

from .models import HierarchicalFlatPage

# The CKEditorWidget requires inline css and javascript, which violate the
# site-wide CSP. This decorator loosens the CSP on the admin pages that load
# the editor widget.
_CSP_UPDATE_DECORATOR = csp_update(
    SCRIPT_SRC="'unsafe-inline'",
    STYLE_SRC=("'unsafe-inline'", "'self'")
)


class HierarchicalFlatPageAdminForm(flatpage_forms.FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta(flatpage_forms.FlatpageForm.Meta):
        model = HierarchicalFlatPage


@method_decorator(_CSP_UPDATE_DECORATOR, name='add_view')
@method_decorator(_CSP_UPDATE_DECORATOR, name='change_view')
class HierarchicalFlatPageAdmin(flatpage_admin.FlatPageAdmin):
    form = HierarchicalFlatPageAdminForm


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(HierarchicalFlatPage, HierarchicalFlatPageAdmin)
