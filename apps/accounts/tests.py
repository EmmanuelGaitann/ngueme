"""Tests — app accounts."""
from django.test import TestCase, Client
from django.urls import reverse
from .models import User


class AccountsViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Alice',
            last_name='Dupont',
            email='alice@example.com',
        )

    # ── Auth ──────────────────────────────────────────────────────────────────

    def test_login_page_loads(self):
        r = self.client.get(reverse('accounts:login'))
        self.assertEqual(r.status_code, 200)

    def test_login_valid(self):
        r = self.client.post(reverse('accounts:login'), {
            'username': 'testuser', 'password': 'testpass123'
        })
        self.assertRedirects(r, reverse('dashboard:home'))

    def test_login_invalid(self):
        r = self.client.post(reverse('accounts:login'), {
            'username': 'testuser', 'password': 'wrongpass'
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.wsgi_request.user.is_authenticated)

    def test_register_page_loads(self):
        r = self.client.get(reverse('accounts:register'))
        self.assertEqual(r.status_code, 200)

    def test_register_creates_user(self):
        r = self.client.post(reverse('accounts:register'), {
            'username': 'nouveau',
            'first_name': 'Nouveau',
            'last_name': 'User',
            'email': 'nouveau@test.com',
            'city': 'Douala',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertTrue(User.objects.filter(username='nouveau').exists())

    def test_logout_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(r, reverse('accounts:login'))

    # ── Profile ───────────────────────────────────────────────────────────────

    def test_profile_requires_login(self):
        r = self.client.get(reverse('accounts:profile'))
        self.assertEqual(r.status_code, 302)

    def test_profile_loads_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.get(reverse('accounts:profile'))
        self.assertEqual(r.status_code, 200)

    def test_profile_update(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Alice', 'last_name': 'Martin',
            'email': 'alice@example.com', 'city': 'Douala',
            'country': 'Cameroun', 'monthly_income_target': 300000,
        })
        self.assertRedirects(r, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, 'Martin')

    # ── Password change ───────────────────────────────────────────────────────

    def test_password_change_page_loads(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(r.status_code, 200)

    def test_password_change_success(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'testpass123',
            'new_password1': 'NewSecure456!',
            'new_password2': 'NewSecure456!',
        })
        self.assertRedirects(r, reverse('accounts:profile'))

    # ── Upgrade ───────────────────────────────────────────────────────────────

    def test_upgrade_page_loads(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.get(reverse('accounts:upgrade'))
        self.assertEqual(r.status_code, 200)

    def test_upgrade_sets_pro_plan(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('accounts:upgrade'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.plan, 'pro')

    def test_upgrade_redirects_if_already_pro(self):
        self.user.plan = 'pro'
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        r = self.client.get(reverse('accounts:upgrade'))
        self.assertRedirects(r, reverse('dashboard:home'))

    # ── Model ─────────────────────────────────────────────────────────────────

    def test_get_initials_two_names(self):
        self.assertEqual(self.user.get_initials(), 'AD')

    def test_default_plan_is_free(self):
        self.assertEqual(self.user.plan, User.PLAN_FREE)
