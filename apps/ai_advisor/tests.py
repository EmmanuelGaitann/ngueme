"""Tests — app ai_advisor."""
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from .models import ChatMessage, AIReport
import datetime


class AIAdvisorViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.login(username='alice', password='pass123')

    def test_advisor_home_loads(self):
        r = self.client.get(reverse('ai_advisor:home'))
        self.assertEqual(r.status_code, 200)

    def test_advisor_home_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('ai_advisor:home'))
        self.assertEqual(r.status_code, 302)

    def test_advisor_home_creates_report(self):
        self.client.get(reverse('ai_advisor:home'))
        self.assertTrue(AIReport.objects.filter(user=self.user).exists())

    def test_chat_view_requires_post(self):
        r = self.client.get(reverse('ai_advisor:chat'))
        self.assertEqual(r.status_code, 405)

    def test_chat_view_empty_message(self):
        import json
        r = self.client.post(
            reverse('ai_advisor:chat'),
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 400)

    def test_chat_saves_messages(self):
        import json
        self.client.post(
            reverse('ai_advisor:chat'),
            data=json.dumps({'message': 'Quel est mon solde ?'}),
            content_type='application/json'
        )
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 2)

    def test_refresh_report(self):
        r = self.client.get(reverse('ai_advisor:refresh_report'))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('report', data)

    def test_parse_sms_ia_empty(self):
        import json
        r = self.client.post(
            reverse('ai_advisor:parse_sms'),
            data=json.dumps({'sms': ''}),
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 400)

    def test_parse_sms_ia_valid(self):
        import json
        r = self.client.post(
            reverse('ai_advisor:parse_sms'),
            data=json.dumps({'sms': 'Vous avez reçu 25000 FCFA de DUPOND Jean via MTN MoMo'}),
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['status'], 'ok')


class AIReportModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_report_str(self):
        today = datetime.date.today()
        report = AIReport.objects.create(
            user=self.user, content='Rapport test', week_start=today
        )
        self.assertIn('alice', str(report))

    def test_unique_together(self):
        today = datetime.date.today()
        AIReport.objects.create(user=self.user, content='v1', week_start=today)
        with self.assertRaises(Exception):
            AIReport.objects.create(user=self.user, content='v2', week_start=today)
