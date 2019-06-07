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

    def has_add_permission(self, request):
        # HierarchicalFlatPage is a proxy to a model that is defined in an
        # external application. As such, Django does not generate a migration
        # to create a permission set for the proxy model as it would for proxies
        # to models defined in the same app. Rather than manually creating a
        # migration to add the required permissions, we piggy-back on the
        # existing permissions for the standard flatpage model.
        #
        # This issue is outlined further in
        # https://code.djangoproject.com/ticket/11154
        return request.user.has_perm('flatpages.add_flatpage')

    def has_view_permission(self, request, obj=None):
        # Same comment as has_add_permission
        return request.user.has_perm('flatpages.view_flatpage')

    def has_change_permission(self, request, obj=None):
        # Same comment as has_add_permission
        return request.user.has_perm('flatpages.add_flatpage')

    def has_delete_permission(self, request, obj=None):
        # Same comment as has_add_permission
        return request.user.has_perm('flatpages.delete_flatpage')

    def has_module_permission(self, request):
        # Same comment as has_add_permission
        return request.user.has_module_perms('flatpages')


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(HierarchicalFlatPage, HierarchicalFlatPageAdmin)
