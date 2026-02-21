import csv
import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Transaction, Category, BudgetLimit, PatrimoineEntry
from .forms import TransactionForm, BudgetLimitForm
from .services import parse_sms as sms_parse


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _is_mobile(request):
    cookie = request.COOKIES.get('finai_view')
    if cookie:
        return cookie == 'mobile'
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    return any(k in ua for k in ('mobile', 'android', 'iphone', 'ipad'))


@login_required
def journal(request):
    qs = Transaction.objects.filter(user=request.user).select_related('category')

    type_filter = request.GET.get('type', '')
    date_from   = request.GET.get('date_from', '')
    date_to     = request.GET.get('date_to', '')

    if type_filter:
        qs = qs.filter(type=type_filter)
    if date_from:
        try:
            qs = qs.filter(date__gte=date.fromisoformat(date_from))
        except ValueError:
            date_from = ''
    if date_to:
        try:
            qs = qs.filter(date__lte=date.fromisoformat(date_to))
        except ValueError:
            date_to = ''

    paginator = Paginator(qs, 25)
    page      = paginator.get_page(request.GET.get('page', 1))
    template  = 'transactions/journal_pwa.html' if _is_mobile(request) else 'transactions/journal.html'
    return render(request, template, {
        'transactions': page,
        'categories':   Category.objects.all(),
        'form':         TransactionForm(),
        'type_filter':  type_filter,
        'date_from':    date_from,
        'date_to':      date_to,
        'total_count':  paginator.count,
    })


@login_required
def analyse(request):
    """Analyse financière sur plage de dates personnalisée."""
    from .services import (
        get_range_stats, get_expense_by_category_range,
        get_daily_series, get_monthly_series,
    )
    today        = date.today()
    default_from = today.replace(day=1).isoformat()
    default_to   = today.isoformat()

    date_from_str = request.GET.get('date_from', default_from)
    date_to_str   = request.GET.get('date_to',   default_to)

    try:
        date_from = date.fromisoformat(date_from_str)
        date_to   = date.fromisoformat(date_to_str)
    except ValueError:
        date_from = date.fromisoformat(default_from)
        date_to   = today

    if date_from > date_to:
        date_from, date_to = date_to, date_from

    days     = (date_to - date_from).days + 1
    stats    = get_range_stats(request.user, date_from, date_to)
    cat_rows = list(get_expense_by_category_range(request.user, date_from, date_to))

    if days <= 60:
        series = get_daily_series(request.user, date_from, date_to)
    else:
        series = get_monthly_series(request.user, months=min(24, days // 28 + 1))

    txs = (Transaction.objects
           .filter(user=request.user, date__gte=date_from, date__lte=date_to,
                   type__in=['income', 'expense'])
           .select_related('category').order_by('-date')[:100])

    cat_data = [{'label': r['category__name'] or 'Divers', 'total': int(r['total'])} for r in cat_rows]

    template = 'transactions/analyse_pwa.html' if _is_mobile(request) else 'transactions/analyse.html'
    return render(request, template, {
        'stats':        stats,
        'date_from':    date_from.isoformat(),
        'date_to':      date_to.isoformat(),
        'series_json':  json.dumps(series),
        'cat_data':     json.dumps(cat_data),
        'transactions': txs,
    })


@login_required
@require_POST
def add_transaction(request):
    form = TransactionForm(request.POST)
    if form.is_valid():
        tx = form.save(commit=False)
        tx.user = request.user
        tx.save()
        if _is_ajax(request):
            return JsonResponse({'status': 'ok', 'id': tx.id})
        messages.success(request, 'Transaction enregistrée.')
    else:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        messages.error(request, 'Formulaire invalide.')
    return redirect('transactions:journal')


@login_required
def edit_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            form.save()
            if _is_ajax(request):
                return JsonResponse({'status': 'ok'})
            messages.success(request, 'Transaction modifiée.')
            return redirect('transactions:journal')
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({
        'id':          tx.id,
        'amount':      int(tx.amount),
        'type':        tx.type,
        'description': tx.description,
        'category':    tx.category_id,
        'date':        tx.date.isoformat(),
        'notes':       tx.notes,
    })


@login_required
@require_POST
def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    tx.delete()
    if _is_ajax(request):
        return JsonResponse({'status': 'ok'})
    messages.success(request, 'Transaction supprimée.')
    return redirect('transactions:journal')


@login_required
@require_POST
def parse_sms_view(request):
    data   = json.loads(request.body)
    result = sms_parse(data.get('sms', ''))
    if result:
        return JsonResponse({'status': 'ok', 'data': result})
    return JsonResponse({'status': 'error', 'message': 'SMS non reconnu'}, status=400)


@login_required
@require_POST
def add_from_sms(request):
    data     = json.loads(request.body)
    category = Category.objects.filter(slug=data.get('category', 'divers')).first()
    tx = Transaction.objects.create(
        user        = request.user,
        amount      = data['amount'],
        type        = data['type'],
        description = data['description'],
        category    = category,
        date        = data.get('date', date.today()),
        source      = 'sms',
        raw_sms     = data.get('raw_sms', ''),
    )
    return JsonResponse({'status': 'ok', 'id': tx.id})


@login_required
def api_list(request):
    txs = Transaction.objects.filter(user=request.user).select_related('category')[:100]
    return JsonResponse({'transactions': [{
        'id':          t.id,
        'amount':      int(t.amount),
        'signed':      int(t.signed_amount),
        'type':        t.type,
        'description': t.description,
        'category':    t.category.name if t.category else 'Divers',
        'cat_icon':    t.category.icon if t.category else 'fa-circle-dot',
        'cat_class':   t.category.color_class if t.category else 'ci-divers',
        'date':        t.date.isoformat(),
        'planned':     t.is_planned,
        'source':      t.source,
    } for t in txs]})


@login_required
def export_csv(request):
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to',   '')
    qs = Transaction.objects.filter(user=request.user).select_related('category').order_by('-date')
    if date_from:
        try:
            qs = qs.filter(date__gte=date.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            qs = qs.filter(date__lte=date.fromisoformat(date_to))
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="finai_transactions.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Date', 'Type', 'Montant (FCFA)', 'Description', 'Catégorie', 'Source', 'Notes'])
    for tx in qs:
        writer.writerow([
            tx.date.strftime('%d/%m/%Y'),
            tx.get_type_display(),
            int(tx.amount),
            tx.description,
            tx.category.name if tx.category else 'Divers',
            tx.get_source_display(),
            tx.notes,
        ])
    return response


# ── Limites budgétaires ────────────────────────────────────────────────────────

@login_required
def budgets(request):
    limits = BudgetLimit.objects.filter(user=request.user).select_related('category')
    form   = BudgetLimitForm()
    if request.method == 'POST':
        form = BudgetLimitForm(request.POST)
        if form.is_valid():
            limit, created = BudgetLimit.objects.get_or_create(
                user=request.user,
                category=form.cleaned_data['category'],
                defaults={'amount': form.cleaned_data['amount']},
            )
            if not created:
                limit.amount = form.cleaned_data['amount']
                limit.save()
            messages.success(request, 'Limite enregistrée.')
            return redirect('transactions:budgets')
    from .services import get_expense_by_category
    spent_map = {
        r['category__slug']: int(r['total'])
        for r in get_expense_by_category(request.user)
    }
    budget_rows = []
    for lim in limits:
        spent = spent_map.get(lim.category.slug, 0)
        pct   = int(spent / lim.amount * 100) if lim.amount > 0 else 0
        budget_rows.append({
            'limit': lim,
            'spent': spent,
            'pct':   min(pct, 100),
            'over':  pct >= 100,
            'warn':  80 <= pct < 100,
        })
    return render(request, 'transactions/budgets.html', {
        'budget_rows': budget_rows,
        'form':        form,
        'categories':  Category.objects.all(),
    })


@login_required
@require_POST
def delete_budget(request, pk):
    limit = get_object_or_404(BudgetLimit, pk=pk, user=request.user)
    limit.delete()
    messages.success(request, 'Limite supprimée.')
    return redirect('transactions:budgets')


# ── Patrimoine ─────────────────────────────────────────────────────────────────

@login_required
def patrimoine(request):
    from .services import get_patrimoine_summary
    from django.db.models import Sum as DSum

    entries = PatrimoineEntry.objects.filter(user=request.user).order_by('-date')
    summary = get_patrimoine_summary(request.user)

    actifs  = entries.filter(ptype='actif')
    passifs = entries.filter(ptype='passif')

    cat_actifs  = list(actifs.values('category').annotate(total=DSum('valeur')).order_by('-total'))
    cat_passifs = list(passifs.values('category').annotate(total=DSum('valeur')).order_by('-total'))

    template = 'transactions/patrimoine_pwa.html' if _is_mobile(request) else 'transactions/patrimoine.html'
    return render(request, template, {
        'summary':    summary,
        'actifs':     actifs,
        'passifs':    passifs,
        'cat_labels': json.dumps([e['category'] for e in cat_actifs] or ['Aucun']),
        'cat_totals': json.dumps([int(e['total']) for e in cat_actifs] or [0]),
        'pas_labels': json.dumps([e['category'] for e in cat_passifs] or ['Aucun']),
        'pas_totals': json.dumps([int(e['total']) for e in cat_passifs] or [0]),
    })


@login_required
@require_POST
def add_patrimoine(request):
    ptype    = request.POST.get('ptype')
    category = request.POST.get('category', 'autre')
    label    = request.POST.get('label', '').strip()
    notes    = request.POST.get('notes', '').strip()
    try:
        valeur = int(request.POST.get('valeur', 0))
        d      = date.fromisoformat(request.POST.get('date', date.today().isoformat()))
    except (ValueError, TypeError):
        messages.error(request, 'Données invalides.')
        return redirect('transactions:patrimoine')

    if not label or valeur <= 0 or ptype not in ('actif', 'passif'):
        messages.error(request, 'Veuillez remplir tous les champs.')
        return redirect('transactions:patrimoine')

    PatrimoineEntry.objects.create(
        user=request.user, ptype=ptype, category=category,
        label=label, valeur=valeur, date=d, notes=notes,
    )
    messages.success(request, 'Entrée patrimoine enregistrée.')
    return redirect('transactions:patrimoine')


@login_required
@require_POST
def delete_patrimoine(request, pk):
    entry = get_object_or_404(PatrimoineEntry, pk=pk, user=request.user)
    entry.delete()
    if _is_ajax(request):
        return JsonResponse({'status': 'ok'})
    messages.success(request, 'Entrée supprimée.')
    return redirect('transactions:patrimoine')


# ── Push Notifications API ─────────────────────────────────────────────────────

@login_required
@require_POST
def push_subscribe(request):
    """Enregistre un abonnement push navigateur."""
    from apps.accounts.models import PushSubscription
    try:
        data = json.loads(request.body)
        sub  = data.get('subscription', {})
        keys = sub.get('keys', {})
        PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=sub['endpoint'],
            defaults={
                'p256dh':     keys.get('p256dh', ''),
                'auth':       keys.get('auth', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:300],
            }
        )
        return JsonResponse({'status': 'ok'})
    except Exception:
        return JsonResponse({'status': 'error'}, status=400)


@login_required
def push_check(request):
    """Retourne les alertes actives pour le push côté client."""
    from .services import get_budget_alerts
    alerts = get_budget_alerts(request.user)
    return JsonResponse({
        'count':    len(alerts),
        'messages': [f'{a["category"]} : {a["pct"]}% du budget' for a in alerts],
    })
