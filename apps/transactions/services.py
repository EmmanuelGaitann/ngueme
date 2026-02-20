"""Services métier FIN.AI — stats, SMS parsing, score."""
import re
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum
from .models import Transaction


def get_monthly_stats(user, year=None, month=None):
    """Stats complètes d'un mois."""
    today = date.today()
    year  = year  or today.year
    month = month or today.month

    qs   = Transaction.objects.filter(user=user, date__year=year, date__month=month)
    real = qs.filter(type__in=['income', 'expense'])

    incomes  = real.filter(type='income').aggregate(t=Sum('amount'))['t']  or Decimal(0)
    expenses = real.filter(type='expense').aggregate(t=Sum('amount'))['t'] or Decimal(0)
    net      = incomes - expenses
    burn     = int(expenses / incomes * 100) if incomes > 0 else 0

    return {
        'incomes':          incomes,
        'expenses':         expenses,
        'net':              net,
        'burn_rate':        burn,
        'free_pct':         max(0, 100 - burn),
        'invest_capacity':  net,
        'planned_exp': qs.filter(type='planned_expense').aggregate(t=Sum('amount'))['t'] or Decimal(0),
        'planned_inc': qs.filter(type='planned_income').aggregate(t=Sum('amount'))['t']  or Decimal(0),
    }


def get_monthly_series(user, months=6):
    """Séries temporelles revenus/dépenses pour les graphiques."""
    today  = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        d  = (today.replace(day=1) - timedelta(days=i * 28))
        qs = Transaction.objects.filter(user=user, date__year=d.year, date__month=d.month, type__in=['income','expense'])
        result.append({
            'label':   d.strftime('%b'),
            'income':  int(qs.filter(type='income').aggregate(t=Sum('amount'))['t']  or 0),
            'expense': int(qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0),
        })
    return result


def get_expense_by_category(user, year=None, month=None):
    today = date.today()
    return (
        Transaction.objects
        .filter(user=user, date__year=year or today.year, date__month=month or today.month, type='expense')
        .values('category__name', 'category__slug', 'category__icon', 'category__color_class')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )


def detect_leaks(user):
    """Top 3 fuites (dépenses les plus lourdes du mois)."""
    rows = list(get_expense_by_category(user))
    return [{
        'category': r['category__name'] or 'Divers',
        'slug':     r['category__slug'] or 'divers',
        'icon':     r['category__icon'] or 'fa-circle-dot',
        'color':    r['category__color_class'] or 'ci-divers',
        'amount':   int(r['total']),
    } for r in rows[:3]]


def compute_score(user):
    """Score FIN.AI sur 100."""
    stats = get_monthly_stats(user)
    if stats['incomes'] == 0:
        return {'total': 0, 'income_grade': '-', 'saving_grade': '-', 'expense_grade': '-'}

    saving_rate = float(stats['net'] / stats['incomes'])
    sp = min(40, int(saving_rate * 50))
    sg = 'A+' if sp >= 35 else ('A' if sp >= 28 else ('B' if sp >= 20 else ('C+' if sp >= 12 else 'C')))

    burn = stats['burn_rate']
    ep = 24 if burn < 30 else (20 if burn < 45 else (14 if burn < 60 else 8))
    eg = 'A' if ep >= 22 else ('B' if ep >= 18 else ('C+' if ep >= 12 else 'C'))

    return {'total': min(100, sp + 28 + ep), 'income_grade': 'A+', 'saving_grade': sg, 'expense_grade': eg}


def get_budget_alerts(user, year=None, month=None):
    """Retourne les catégories qui approchent ou dépassent leur limite (≥ 80%)."""
    from .models import BudgetLimit
    today = date.today()
    year  = year  or today.year
    month = month or today.month
    alerts = []
    for lim in BudgetLimit.objects.filter(user=user).select_related('category'):
        spent = (Transaction.objects
                 .filter(user=user, category=lim.category, type='expense',
                         date__year=year, date__month=month)
                 .aggregate(t=Sum('amount'))['t'] or Decimal(0))
        pct = int(spent / lim.amount * 100) if lim.amount > 0 else 0
        if pct >= 80:
            alerts.append({
                'category': lim.category.name,
                'slug':     lim.category.slug,
                'icon':     lim.category.icon,
                'color':    lim.category.color_class,
                'limit':    int(lim.amount),
                'spent':    int(spent),
                'pct':      pct,
                'over':     pct >= 100,
            })
    return alerts


def get_range_stats(user, date_from, date_to):
    """Stats sur une plage de dates personnalisée."""
    qs   = Transaction.objects.filter(user=user, date__gte=date_from, date__lte=date_to)
    real = qs.filter(type__in=['income', 'expense'])
    incomes  = real.filter(type='income').aggregate(t=Sum('amount'))['t']  or Decimal(0)
    expenses = real.filter(type='expense').aggregate(t=Sum('amount'))['t'] or Decimal(0)
    net  = incomes - expenses
    burn = int(expenses / incomes * 100) if incomes > 0 else 0
    return {
        'incomes': incomes, 'expenses': expenses, 'net': net,
        'burn_rate': burn, 'free_pct': max(0, 100 - burn),
        'tx_count':  real.count(),
        'days':      (date_to - date_from).days + 1,
    }


def get_expense_by_category_range(user, date_from, date_to):
    """Dépenses par catégorie sur une plage."""
    return (
        Transaction.objects
        .filter(user=user, date__gte=date_from, date__lte=date_to, type='expense')
        .values('category__name', 'category__slug', 'category__icon', 'category__color_class')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )


def get_daily_series(user, date_from, date_to):
    """Séries journalières pour courte plage (≤ 60 jours)."""
    result  = []
    current = date_from
    while current <= date_to:
        qs = Transaction.objects.filter(user=user, date=current, type__in=['income', 'expense'])
        result.append({
            'label':   current.strftime('%d/%m'),
            'income':  int(qs.filter(type='income').aggregate(t=Sum('amount'))['t']  or 0),
            'expense': int(qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0),
        })
        current += timedelta(days=1)
    return result


def get_patrimoine_summary(user):
    """Actifs − Passifs = Patrimoine net."""
    from .models import PatrimoineEntry
    actifs  = PatrimoineEntry.objects.filter(user=user, ptype='actif').aggregate(t=Sum('valeur'))['t']  or Decimal(0)
    passifs = PatrimoineEntry.objects.filter(user=user, ptype='passif').aggregate(t=Sum('valeur'))['t'] or Decimal(0)
    return {'actifs': actifs, 'passifs': passifs, 'net': actifs - passifs}


def parse_sms(sms_text):
    """Parse un SMS Mobile Money (regex, sans IA)."""
    if not sms_text or len(sms_text) < 10:
        return None
    am = re.search(r'(\d[\d\s]{1,10})\s*(?:F CFA|FCFA|XAF)', sms_text, re.IGNORECASE)
    if not am:
        return None
    amount    = int(am.group(1).replace(' ', ''))
    is_income = bool(re.search(r'\b(reçu|received|crédit|crédité|déposé)\b', sms_text, re.IGNORECASE))
    network   = ('MTN MoMo' if re.search(r'\bMTN\b', sms_text, re.IGNORECASE)
                 else 'Orange Money' if re.search(r'\bOrange\b', sms_text, re.IGNORECASE)
                 else 'Mobile Money')
    sender_m  = re.search(r'(?:de|from)\s+([A-Z][a-zA-Z\s]{2,25})', sms_text)
    sender    = sender_m.group(1).strip() if sender_m else network
    return {
        'amount':      amount,
        'type':        'income' if is_income else 'expense',
        'description': f'{"Reçu de" if is_income else "Envoyé à"} {sender}',
        'network':     network,
        'raw_sms':     sms_text,
        'date':        date.today().isoformat(),
        'source':      'sms',
    }
