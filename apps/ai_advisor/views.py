import json
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import ChatMessage, AIReport
from .services import weekly_report, chat, predictions, parse_sms_ai


def _is_mobile(request):
    cookie = request.COOKIES.get('finai_view')
    if cookie:
        return cookie == 'mobile'
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    return any(k in ua for k in ('mobile', 'android', 'iphone', 'ipad'))


@login_required
def advisor_home(request):
    week_start = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    report_obj, _ = AIReport.objects.get_or_create(
        user=request.user, week_start=week_start,
        defaults={'content': weekly_report(request.user)}
    )
    history = list(ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:10])
    preds   = predictions(request.user)
    template = 'ai_advisor/advisor_pwa.html' if _is_mobile(request) else 'ai_advisor/advisor.html'
    return render(request, template, {
        'report':      report_obj.content,
        'history':     reversed(history),
        'predictions': preds,
        'has_api_key': bool(settings.ANTHROPIC_API_KEY),
    })


@login_required
@require_POST
def chat_view(request):
    data     = json.loads(request.body)
    question = data.get('message', '').strip()
    if not question:
        return JsonResponse({'status': 'error'}, status=400)
    recent  = list(ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:6])
    history = [{'role': m.role, 'content': m.content} for m in reversed(recent)]
    answer  = chat(request.user, question, history)
    ChatMessage.objects.create(user=request.user, role='user',      content=question)
    ChatMessage.objects.create(user=request.user, role='assistant', content=answer)
    return JsonResponse({'status': 'ok', 'answer': answer})


@login_required
@require_POST
def parse_sms_ia(request):
    data   = json.loads(request.body)
    sms    = data.get('sms', '').strip()
    if not sms:
        return JsonResponse({'status': 'error', 'message': 'SMS vide'}, status=400)
    result = parse_sms_ai(request.user, sms)
    if result:
        return JsonResponse({'status': 'ok', 'data': result})
    return JsonResponse({'status': 'error', 'message': 'SMS non reconnu'}, status=400)


@login_required
def refresh_report(request):
    week_start = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    AIReport.objects.filter(user=request.user, week_start=week_start).delete()
    content = weekly_report(request.user)
    AIReport.objects.create(user=request.user, week_start=week_start, content=content)
    return JsonResponse({'status': 'ok', 'report': content})
