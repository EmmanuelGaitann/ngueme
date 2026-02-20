"""Tests — app transactions."""
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from .models import Transaction, Category, BudgetLimit
from .services import get_monthly_stats, compute_score, get_budget_alerts, parse_sms
import datetime


class TransactionViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.login(username='alice', password='pass123')
        self.cat = Category.objects.create(name='Alimentation', slug='alimentation')

    # ── Journal ───────────────────────────────────────────────────────────────

    def test_journal_loads(self):
        r = self.client.get(reverse('transactions:journal'))
        self.assertEqual(r.status_code, 200)

    def test_journal_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('transactions:journal'))
        self.assertEqual(r.status_code, 302)

    def test_journal_pagination(self):
        for i in range(30):
            Transaction.objects.create(
                user=self.user, amount=1000, type='expense',
                description=f'Dépense {i}', date=datetime.date.today()
            )
        r = self.client.get(reverse('transactions:journal'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['transactions'].has_other_pages())

    # ── Add ───────────────────────────────────────────────────────────────────

    def test_add_transaction(self):
        r = self.client.post(reverse('transactions:add'), {
            'amount': 50000, 'type': 'income',
            'description': 'Salaire', 'date': datetime.date.today(),
            'category': self.cat.id,
        })
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 1)

    def test_add_transaction_invalid(self):
        r = self.client.post(reverse('transactions:add'), {
            'amount': '', 'type': 'income', 'description': '',
        })
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 0)

    # ── Edit ─────────────────────────────────────────────────────────────────

    def test_edit_get_returns_json(self):
        tx = Transaction.objects.create(
            user=self.user, amount=10000, type='expense',
            description='Test', date=datetime.date.today()
        )
        r = self.client.get(reverse('transactions:edit', args=[tx.pk]))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['amount'], 10000)
        self.assertEqual(data['description'], 'Test')

    def test_edit_post_updates(self):
        tx = Transaction.objects.create(
            user=self.user, amount=10000, type='expense',
            description='Avant', date=datetime.date.today()
        )
        self.client.post(
            reverse('transactions:edit', args=[tx.pk]),
            {'amount': 20000, 'type': 'expense', 'description': 'Après',
             'date': datetime.date.today()},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        tx.refresh_from_db()
        self.assertEqual(tx.amount, 20000)
        self.assertEqual(tx.description, 'Après')

    def test_edit_other_user_returns_404(self):
        other = User.objects.create_user(username='bob', password='pass123')
        tx = Transaction.objects.create(
            user=other, amount=5000, type='expense',
            description='Bob', date=datetime.date.today()
        )
        r = self.client.get(reverse('transactions:edit', args=[tx.pk]))
        self.assertEqual(r.status_code, 404)

    # ── Delete ────────────────────────────────────────────────────────────────

    def test_delete_transaction(self):
        tx = Transaction.objects.create(
            user=self.user, amount=1000, type='expense',
            description='À supprimer', date=datetime.date.today()
        )
        self.client.post(
            reverse('transactions:delete', args=[tx.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(Transaction.objects.filter(pk=tx.pk).exists())

    # ── Export CSV ────────────────────────────────────────────────────────────

    def test_export_csv(self):
        Transaction.objects.create(
            user=self.user, amount=25000, type='income',
            description='Salaire', date=datetime.date.today()
        )
        r = self.client.get(reverse('transactions:export_csv'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/csv', r['Content-Type'])

    # ── Budgets ───────────────────────────────────────────────────────────────

    def test_budgets_page_loads(self):
        r = self.client.get(reverse('transactions:budgets'))
        self.assertEqual(r.status_code, 200)

    def test_create_budget_limit(self):
        self.client.post(reverse('transactions:budgets'), {
            'category': self.cat.id, 'amount': 100000
        })
        self.assertTrue(BudgetLimit.objects.filter(user=self.user, category=self.cat).exists())

    def test_create_budget_limit_updates_existing(self):
        BudgetLimit.objects.create(user=self.user, category=self.cat, amount=50000)
        self.client.post(reverse('transactions:budgets'), {
            'category': self.cat.id, 'amount': 150000
        })
        lim = BudgetLimit.objects.get(user=self.user, category=self.cat)
        self.assertEqual(int(lim.amount), 150000)

    def test_delete_budget(self):
        lim = BudgetLimit.objects.create(user=self.user, category=self.cat, amount=50000)
        self.client.post(reverse('transactions:delete_budget', args=[lim.pk]))
        self.assertFalse(BudgetLimit.objects.filter(pk=lim.pk).exists())


class TransactionServicesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.cat  = Category.objects.create(name='Loisirs', slug='loisirs')

    def test_monthly_stats_empty(self):
        stats = get_monthly_stats(self.user)
        self.assertEqual(stats['incomes'], 0)
        self.assertEqual(stats['expenses'], 0)
        self.assertEqual(stats['net'], 0)

    def test_monthly_stats_with_data(self):
        today = datetime.date.today()
        Transaction.objects.create(user=self.user, amount=200000, type='income',  description='Salaire', date=today)
        Transaction.objects.create(user=self.user, amount=80000,  type='expense', description='Loyer',   date=today)
        stats = get_monthly_stats(self.user)
        self.assertEqual(int(stats['incomes']),  200000)
        self.assertEqual(int(stats['expenses']), 80000)
        self.assertEqual(int(stats['net']),      120000)
        self.assertEqual(stats['burn_rate'], 40)

    def test_compute_score_no_income(self):
        score = compute_score(self.user)
        self.assertEqual(score['total'], 0)

    def test_budget_alert_triggered(self):
        today = datetime.date.today()
        BudgetLimit.objects.create(user=self.user, category=self.cat, amount=100000)
        Transaction.objects.create(
            user=self.user, amount=85000, type='expense',
            description='Sortie', category=self.cat, date=today
        )
        alerts = get_budget_alerts(self.user)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['pct'], 85)

    def test_budget_alert_not_triggered_below_80(self):
        today = datetime.date.today()
        BudgetLimit.objects.create(user=self.user, category=self.cat, amount=100000)
        Transaction.objects.create(
            user=self.user, amount=50000, type='expense',
            description='Sortie', category=self.cat, date=today
        )
        alerts = get_budget_alerts(self.user)
        self.assertEqual(len(alerts), 0)

    def test_parse_sms_mtn(self):
        sms = 'Vous avez reçu 25000 FCFA de DUPOND Jean via MTN MoMo'
        result = parse_sms(sms)
        self.assertIsNotNone(result)
        self.assertEqual(result['amount'], 25000)
        self.assertEqual(result['type'], 'income')
        self.assertEqual(result['network'], 'MTN MoMo')

    def test_parse_sms_invalid(self):
        result = parse_sms('Bonjour')
        self.assertIsNone(result)
