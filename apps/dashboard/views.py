import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.transactions.models import Transaction
from apps.transactions.services import (
    get_monthly_stats, get_monthly_series,
    get_expense_by_category, detect_leaks, compute_score
)
from apps.ai_advisor.services import predictions


def _is_mobile(request):
    """Détecte mobile via cookie (priorité) puis User-Agent en fallback."""
    cookie = request.COOKIES.get('finai_view')
    if cookie:
        return cookie == 'mobile'
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    return any(k in ua for k in ('mobile', 'android', 'iphone', 'ipad'))


@login_required
def home(request):
    mobile = _is_mobile(request)

    stats      = get_monthly_stats(request.user)
    score      = compute_score(request.user)
    series     = get_monthly_series(request.user)
    leaks      = detect_leaks(request.user)
    cat_rows   = list(get_expense_by_category(request.user))
    recent_txs = Transaction.objects.filter(user=request.user).select_related('category')[:6]
    preds      = predictions(request.user)

    score_offset = int(239 - (score['total'] / 100 * 239))
    cat_data = [{'label': r['category__name'] or 'Divers', 'total': int(r['total'])} for r in cat_rows]

    ctx = {
        'stats': stats, 'score': score, 'score_offset': score_offset,
        'series': series, 'series_json': json.dumps(series),
        'leaks': leaks, 'cat_data': json.dumps(cat_data),
        'recent_transactions': recent_txs, 'predictions': preds,
        'has_api_key': bool(__import__('django.conf', fromlist=['settings']).settings.ANTHROPIC_API_KEY),
    }

    if mobile:
        return render(request, 'dashboard/pwa.html', ctx)
    return render(request, 'dashboard/desktop.html', ctx)


@login_required
def pwa_force(request):
    stats  = get_monthly_stats(request.user)
    score  = compute_score(request.user)
    series = get_monthly_series(request.user)
    leaks  = detect_leaks(request.user)
    return render(request, 'dashboard/pwa.html', {
        'stats': stats, 'score': score,
        'series': series, 'series_json': json.dumps(series), 'leaks': leaks,
    })


def offline(request):
    return render(request, 'dashboard/offline.html', status=200)


@login_required
def simulateur(request):
    """Page simulateur avec produits locaux d'Afrique Centrale."""
    stats = get_monthly_stats(request.user)
    return render(request, 'dashboard/simulateur.html', {
        'invest_capacity': int(stats['invest_capacity']),
    })
