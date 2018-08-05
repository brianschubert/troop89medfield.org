from django.views.generic import DetailView, ListView

from .models import Patrol


class PatrolArchiveView(ListView):
    model = Patrol


class PatrolDetailView(DetailView):
    model = Patrol

    def get_queryset(self):
        return (
            super().get_queryset()
                .prefetch_related('memberships__scout__user')
                .prefetch_related('memberships__term')
        )
