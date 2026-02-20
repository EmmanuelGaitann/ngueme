from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('connexion/',    views.login_view,           name='login'),
    path('inscription/',  views.register_view,        name='register'),
    path('deconnexion/',  views.logout_view,           name='logout'),
    path('profil/',       views.profile_view,          name='profile'),
    path('mot-de-passe/', views.password_change_view,  name='password_change'),
    path('upgrade/',      views.upgrade_view,          name='upgrade'),
]
