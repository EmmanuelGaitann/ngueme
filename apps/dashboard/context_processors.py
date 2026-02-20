from django.conf import settings
from apps.transactions.services import get_monthly_stats, compute_score, get_budget_alerts


def finai_context(request):
    """Injecte les stats globales, alertes et config push dans tous les templates."""
    if not request.user.is_authenticated:
        return {'vapid_public_key': getattr(settings, 'VAPID_PUBLIC_KEY', '')}
    stats  = get_monthly_stats(request.user)
    score  = compute_score(request.user)
    alerts = get_budget_alerts(request.user)
    return {
        'global_stats':    stats,
        'global_score':    score,
        'budget_alerts':   alerts,
        'alert_count':     len(alerts),
        'vapid_public_key': getattr(settings, 'VAPID_PUBLIC_KEY', ''),
    }
