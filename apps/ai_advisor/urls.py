from django.urls import path
from . import views

app_name = 'ai_advisor'

urlpatterns = [
    path('',              views.advisor_home,  name='home'),
    path('chat/',         views.chat_view,     name='chat'),
    path('parse-sms/',    views.parse_sms_ia,  name='parse_sms'),
    path('rapport/sync/', views.refresh_report, name='refresh_report'),
]
