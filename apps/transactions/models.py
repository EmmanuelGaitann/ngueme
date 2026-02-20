from django.db import models
from django.conf import settings
from decimal import Decimal


class Category(models.Model):
    name        = models.CharField('Nom', max_length=100)
    slug        = models.SlugField(unique=True)
    icon        = models.CharField('Icône FA', max_length=60, default='fa-circle-dot')
    color_class = models.CharField('Classe CSS', max_length=40, default='ci-divers')

    class Meta:
        verbose_name = 'Catégorie'
        ordering     = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TYPE_EXPENSE         = 'expense'
    TYPE_INCOME          = 'income'
    TYPE_PLANNED_EXPENSE = 'planned_expense'
    TYPE_PLANNED_INCOME  = 'planned_income'
    TYPE_CHOICES = [
        (TYPE_EXPENSE,         'Dépense'),
        (TYPE_INCOME,          'Revenu'),
        (TYPE_PLANNED_EXPENSE, 'Dépense planifiée'),
        (TYPE_PLANNED_INCOME,  'Revenu attendu'),
    ]
    SOURCE_MANUAL = 'manual'
    SOURCE_SMS    = 'sms'
    SOURCE_AI     = 'ai'
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, 'Saisie manuelle'),
        (SOURCE_SMS,    'SMS Mobile Money'),
        (SOURCE_AI,     'Extrait par IA'),
    ]

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount      = models.DecimalField('Montant', max_digits=15, decimal_places=0)
    type        = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default=TYPE_EXPENSE)
    description = models.CharField('Description', max_length=300)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    date        = models.DateField('Date')
    source      = models.CharField('Source', max_length=10, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    raw_sms     = models.TextField('SMS original', blank=True)
    notes       = models.TextField('Notes', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transaction'
        ordering     = ['-date', '-created_at']

    @property
    def is_expense(self):
        return self.type in (self.TYPE_EXPENSE, self.TYPE_PLANNED_EXPENSE)

    @property
    def is_planned(self):
        return self.type in (self.TYPE_PLANNED_EXPENSE, self.TYPE_PLANNED_INCOME)

    @property
    def signed_amount(self):
        return -self.amount if self.is_expense else self.amount

    def __str__(self):
        s = '-' if self.is_expense else '+'
        return f'{s}{self.amount} FCFA — {self.description}'


class PatrimoineEntry(models.Model):
    PTYPE_CHOICES = [('actif', 'Actif'), ('passif', 'Passif')]
    CAT_CHOICES = [
        ('immobilier',     'Immobilier'),
        ('business',       'Business / Entreprise'),
        ('epargne',        'Épargne / Liquidités'),
        ('investissement', 'Investissement (BVMAC)'),
        ('vehicule',       'Véhicule'),
        ('dette',          'Dette / Emprunt'),
        ('credit',         'Crédit'),
        ('autre',          'Autre'),
    ]
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patrimoine')
    ptype      = models.CharField('Type', max_length=10, choices=PTYPE_CHOICES)
    category   = models.CharField('Catégorie', max_length=20, choices=CAT_CHOICES, default='autre')
    label      = models.CharField('Libellé', max_length=200)
    valeur     = models.DecimalField('Valeur (FCFA)', max_digits=15, decimal_places=0)
    date       = models.DateField("Date d'évaluation")
    notes      = models.TextField('Notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Entrée patrimoine'
        ordering     = ['-date', '-created_at']

    @property
    def is_actif(self):
        return self.ptype == 'actif'

    def __str__(self):
        return f'{self.get_ptype_display()} — {self.label}: {self.valeur} FCFA'


class BudgetLimit(models.Model):
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_limits')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount   = models.DecimalField('Limite', max_digits=15, decimal_places=0)

    class Meta:
        unique_together = ('user', 'category')
        verbose_name    = 'Limite budgétaire'

    def __str__(self):
        return f'{self.user} — {self.category}: {self.amount} FCFA'
