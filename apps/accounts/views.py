from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import LoginForm, RegisterForm, ProfileForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'dashboard:home'))
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Bienvenue {user.first_name} ! Votre espace FIN.AI est prêt.')
        return redirect('dashboard:home')
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profil mis à jour.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def password_change_view(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, 'Mot de passe modifié avec succès.')
        return redirect('accounts:profile')
    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def upgrade_view(request):
    if request.user.plan == 'pro':
        return redirect('dashboard:home')
    if request.method == 'POST':
        request.user.plan = 'pro'
        request.user.save(update_fields=['plan'])
        messages.success(request, 'Bienvenue sur le Plan Pro ! Toutes les fonctionnalités sont débloquées.')
        return redirect('dashboard:home')
    return render(request, 'accounts/upgrade.html')
