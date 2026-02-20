"""
FIN.AI — Point d'entrée Passenger pour O2Switch
Ce fichier est requis par le serveur Passenger utilisé sur l'hébergement O2Switch.
"""
import os
import sys

# Chemin vers le projet (O2Switch le configure automatiquement via cPanel)
# Si besoin, décommentez et adaptez la ligne suivante :
# sys.path.insert(0, '/home/VOTRE_LOGIN_O2SWITCH/CHEMIN_VERS_LE_PROJET')

os.environ['DJANGO_SETTINGS_MODULE'] = 'finai.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
