from django.urls import path

from . import views

app_name = 'trooporg'

urlpatterns = [
    path('patrols/<slug:slug>/', views.PatrolDetailView.as_view(), name='patrol-detail')
]
