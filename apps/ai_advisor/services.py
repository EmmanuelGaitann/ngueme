"""FIN.AI — Service IA (Claude API)."""
import json
from django.conf import settings
from apps.transactions.services import get_monthly_stats, detect_leaks, compute_score


def _client():
    if not settings.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    except ImportError:
        return None


def _context(user):
    stats = get_monthly_stats(user)
    score = compute_score(user)
    leaks = detect_leaks(user)
    leaks_txt = '\n'.join(f"  - {l['category']}: -{l['amount']:,} FCFA" for l in leaks) or '  - Aucune détectée'
    return f"""PROFIL DE {user.get_full_name() or user.username} ({user.city}, {user.country})
Profession: {user.profession or 'Non renseignée'}

MOIS EN COURS:
  Revenus:    {int(stats['incomes']):,} FCFA
  Dépenses:   {int(stats['expenses']):,} FCFA
  Solde net:  {int(stats['net']):,} FCFA
  Burn rate:  {stats['burn_rate']}%
  Capacité:   {int(stats['invest_capacity']):,} FCFA

SCORE FINAI: {score['total']}/100
  Revenus: {score['income_grade']} | Épargne: {score['saving_grade']} | Dépenses: {score['expense_grade']}

FUITES DÉTECTÉES:
{leaks_txt}

Contexte: Afrique Centrale, FCFA, BVMAC disponible."""


def weekly_report(user):
    """Rapport hebdomadaire IA personnalisé."""
    c = _client()
    if not c:
        return _fallback_report(user)
    try:
        r = c.messages.create(
            model=settings.AI_MODEL,
            max_tokens=settings.AI_MAX_TOKENS,
            messages=[{'role': 'user', 'content': f"""{_context(user)}

Rédigez un rapport CFO hebdomadaire en français, personnel et direct (tutoyer).
3 paragraphes courts: bilan semaine, alerte principale, recommandation concrète.
Max 180 mots. Pas de titres."""}]
        )
        return r.content[0].text
    except Exception:
        return _fallback_report(user)


def chat(user, question, history=None):
    """Répond à une question financière."""
    c = _client()
    if not c:
        return _fallback_chat()
    msgs = list(history or [])
    msgs.append({'role': 'user', 'content': question})
    try:
        r = c.messages.create(
            model=settings.AI_MODEL,
            max_tokens=settings.AI_MAX_TOKENS,
            system=f"""Tu es le CFO personnel de {user.get_full_name() or user.username}.
{_context(user)}
Réponds en français, max 150 mots, ancré dans la réalité (FCFA, BVMAC, MoMo).
Ne garantis pas de rendements. Sois direct et pratique.""",
            messages=msgs
        )
        return r.content[0].text
    except Exception:
        return _fallback_chat()


def parse_sms_ai(user, sms_text):
    """Parse SMS avec IA (fallback regex si IA indisponible)."""
    c = _client()
    if not c:
        from apps.transactions.services import parse_sms
        return parse_sms(sms_text)
    try:
        r = c.messages.create(
            model=settings.AI_MODEL,
            max_tokens=200,
            messages=[{'role': 'user', 'content': f"""Extrais les infos de ce SMS Mobile Money camerounais.
Réponds UNIQUEMENT en JSON valide, sans texte autour.
SMS: "{sms_text}"
JSON: {{"amount":<int FCFA>,"type":"income"|"expense","description":"<court>","network":"MTN MoMo"|"Orange Money"|"Mobile Money","date":"<YYYY-MM-DD>|null"}}"""}]
        )
        text = r.content[0].text.strip().replace('```json','').replace('```','').strip()
        data = json.loads(text)
        data['source']  = 'ai'
        data['raw_sms'] = sms_text
        return data
    except Exception:
        from apps.transactions.services import parse_sms
        return parse_sms(sms_text)


def predictions(user):
    """Prédictions 30 jours."""
    c = _client()
    if not c:
        return _fallback_preds(user)
    try:
        r = c.messages.create(
            model=settings.AI_MODEL,
            max_tokens=300,
            messages=[{'role': 'user', 'content': f"""{_context(user)}
Génère des prédictions 30 jours. JSON uniquement:
{{"predicted_balance":<int>,"balance_change":<int>,"risk_level":"Faible"|"Moyen"|"Élevé","risk_detail":"<court>","best_invest_date":"<YYYY-MM-DD>","best_invest_reason":"<court>"}}"""}]
        )
        text = r.content[0].text.strip().replace('```json','').replace('```','').strip()
        return json.loads(text)
    except Exception:
        return _fallback_preds(user)


# ── Fallbacks ─────────────────────────────────────────────────────────────────

def _fallback_report(user):
    s = get_monthly_stats(user)
    return (f"Ce mois, ton solde net est {int(s['net']):,} FCFA (burn rate {s['burn_rate']}%). "
            f"Tes revenus de {int(s['incomes']):,} FCFA couvrent bien tes dépenses. "
            f"Ta capacité d'investissement de {int(s['invest_capacity']):,} FCFA mérite d'être orientée vers des obligations BVMAC à 6%. "
            f"Configure ta clé ANTHROPIC_API_KEY pour des analyses personnalisées.")


def _fallback_chat():
    return ("Configurez votre clé ANTHROPIC_API_KEY dans .env pour activer le conseiller IA. "
            "En attendant, explorez les onglets Diagnostic et Simulateur pour vos analyses.")


def _fallback_preds(user):
    s = get_monthly_stats(user)
    n = int(s['net'])
    return {
        'predicted_balance':  n + int(n * 0.05),
        'balance_change':     int(n * 0.05),
        'risk_level':         'Faible' if s['burn_rate'] < 50 else 'Moyen',
        'risk_detail':        'Basé sur vos habitudes récentes',
        'best_invest_date':   '2026-03-01',
        'best_invest_reason': 'Prochain appel d\'offres BVMAC estimé',
    }
