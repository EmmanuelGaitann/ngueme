from functools import wraps
from django.shortcuts import redirect


def pro_required(view_func):
    """Restreint l'accès aux utilisateurs avec le plan Pro."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.plan != 'pro':
            return redirect('accounts:upgrade')
        return view_func(request, *args, **kwargs)
    return _wrapped
