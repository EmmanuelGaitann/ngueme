# FIN.AI — CFO Autonome pour l'Afrique Centrale

Application Django complète avec interface Desktop et PWA Mobile.

---

## Installation en 5 étapes

### 1. Prérequis
```
Python 3.10 ou supérieur
pip
```

### 2. Environnement virtuel et dépendances
```bash
cd finai_project
python -m venv venv

# Activer (Linux / Mac)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos valeurs
# SECRET_KEY : générez une clé avec : python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# ANTHROPIC_API_KEY : votre clé sur https://console.anthropic.com
```

### 4. Base de données
```bash
# Créer les tables
python manage.py migrate

# Charger les catégories (obligatoire)
python manage.py loaddata fixtures/categories.json

# Créer un compte admin
python manage.py createsuperuser
```

### 5. Lancer
```bash
python manage.py runserver
```

Ouvrir : **http://127.0.0.1:8000**

---

## Structure du projet

```
finai_project/
├── finai/
│   ├── settings/
│   │   ├── __init__.py      ← importe base.py
│   │   └── base.py          ← configuration Django
│   ├── urls.py              ← routes principales
│   └── wsgi.py
│
├── apps/
│   ├── accounts/            ← authentification, profil
│   ├── dashboard/           ← tableau de bord (desktop + PWA)
│   ├── transactions/        ← journal, SMS parser, CRUD
│   └── ai_advisor/          ← assistant Claude, rapports IA
│
├── static/
│   ├── css/
│   │   ├── finai.css        ← styles desktop + auth
│   │   └── pwa.css          ← styles mobile
│   └── js/
│       └── finai.js         ← JavaScript partagé (charts, SMS)
│
├── templates/
│   ├── base_desktop.html    ← layout avec sidebar
│   ├── base_pwa.html        ← layout mobile
│   ├── accounts/            ← login, register, profile
│   ├── dashboard/           ← desktop.html, pwa.html
│   ├── transactions/        ← journal.html
│   ├── ai_advisor/          ← advisor.html
│   └── partials/            ← composants réutilisables
│
├── fixtures/
│   └── categories.json      ← 9 catégories de transactions
│
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Fonctionnalités

### Interface Desktop (navigateur PC)
- Sidebar fixe avec navigation 5 onglets
- Dashboard avec sparkline, score FIN.AI, revenus/dépenses
- Journal de caisse avec parser SMS intégré
- Assistant IA avec chat (Claude Haiku)

### Interface PWA Mobile (smartphone)
- Détection automatique mobile/desktop
- Navigation bottom bar
- Installable sur écran d'accueil (Add to Home Screen)

### Intelligence Artificielle
- Parser SMS Mobile Money (MTN MoMo, Orange Money)
- Rapport hebdomadaire personnalisé
- Chat financier (questions/réponses)
- Prédictions 30 jours
- Fallback automatique si clé API non configurée

---

## Coûts IA estimés

| Modèle configuré | Coût / 1 000 transactions |
|---|---|
| claude-haiku-4-5-20251001 | ~160 FCFA |
| Fallback (sans API key) | 0 FCFA |

500 utilisateurs actifs ≈ 80 000 FCFA/mois en coûts IA

---

## Déploiement O2switch

```bash
# En production
DEBUG=False
ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Gunicorn
gunicorn finai.wsgi:application --bind 0.0.0.0:8000
```

---

## Prochaines étapes suggérées

1. Ajout de la page Diagnostic (graphiques + fuites)
2. Page Simulateur de patrimoine
3. Plans Free/Pro (Stripe)
4. Notifications email (rapport hebdomadaire)
5. Export PDF du bilan mensuel
