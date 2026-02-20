"""Tests — app dashboard."""
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User


class DashboardViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_dashboard_requires_login(self):
        r = self.client.get(reverse('dashboard:home'))
        self.assertEqual(r.status_code, 302)

    def test_dashboard_loads(self):
        self.client.login(username='alice', password='pass123')
        r = self.client.get(reverse('dashboard:home'))
        self.assertEqual(r.status_code, 200)

    def test_dashboard_has_stats(self):
        self.client.login(username='alice', password='pass123')
        r = self.client.get(reverse('dashboard:home'))
        self.assertIn('stats', r.context)
        self.assertIn('score', r.context)

    def test_root_redirects_to_dashboard(self):
        self.client.login(username='alice', password='pass123')
        r = self.client.get('/')
        self.assertEqual(r.status_code, 302)

    def test_pwa_view(self):
        self.client.login(username='alice', password='pass123')
        r = self.client.get(reverse('dashboard:pwa'))
        self.assertEqual(r.status_code, 200)
