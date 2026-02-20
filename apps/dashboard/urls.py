from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',             RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
    path('dashboard/',   views.home,        name='home'),
    path('mobile/',      views.pwa_force,   name='pwa'),
    path('offline/',     views.offline,     name='offline'),
    path('simulateur/',  views.simulateur,  name='simulateur'),
]
