"""
FIN.AI — Point d'entrée Passenger pour O2Switch
"""
import os
import sys
from pathlib import Path

# Chemin absolu du projet sur O2Switch
PROJECT_PATH = '/home/sc1koga4651/ngueme.ravisa.org'

# Ajouter le projet au Python path
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Charger le .env explicitement avant Django
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_PATH, '.env'))

# Définir les settings de production
os.environ['DJANGO_SETTINGS_MODULE'] = 'finai.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
