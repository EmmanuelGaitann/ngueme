from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur FIN.AI — étend le modèle Django standard."""

    phone      = models.CharField('Téléphone', max_length=20, blank=True)
    city       = models.CharField('Ville', max_length=100, blank=True, default='Yaoundé')
    country    = models.CharField('Pays', max_length=100, blank=True, default='Cameroun')
    profession = models.CharField('Profession', max_length=200, blank=True)
    avatar     = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True)

    monthly_income_target = models.DecimalField(
        'Objectif revenu mensuel', max_digits=15, decimal_places=0, default=0
    )

    PLAN_FREE = 'free'
    PLAN_PRO  = 'pro'
    PLAN_CHOICES = [(PLAN_FREE, 'Gratuit'), (PLAN_PRO, 'Pro')]
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default=PLAN_FREE)

    class Meta:
        verbose_name         = 'Utilisateur'
        verbose_name_plural  = 'Utilisateurs'

    def get_initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return (self.username[:2]).upper()

    def __str__(self):
        return self.get_full_name() or self.username


class PushSubscription(models.Model):
    """Abonnement Web Push par navigateur/appareil."""
    user       = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint   = models.TextField('Endpoint')
    p256dh     = models.TextField('Clé p256dh')
    auth       = models.TextField('Clé auth')
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name    = 'Abonnement Push'
        unique_together = ('user', 'endpoint')

    def __str__(self):
        return f'Push — {self.user} — {self.endpoint[:60]}'
