"""
Management command : génère les clés VAPID pour les notifications push.
Usage : python manage.py generate_vapid_keys
"""
import base64
from django.core.management.base import BaseCommand
from py_vapid import Vapid01
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


class Command(BaseCommand):
    help = 'Génère les clés VAPID pour Web Push Notifications'

    def handle(self, *args, **options):
        v = Vapid01()
        v.generate_keys()

        private_pem = v.private_pem().decode('utf-8').strip()
        pub_bytes   = v._public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        public_key  = base64.urlsafe_b64encode(pub_bytes).decode('utf-8').rstrip('=')

        self.stdout.write(self.style.SUCCESS('\n✅ Clés VAPID générées — ajoutez dans .env :\n'))
        self.stdout.write(self.style.WARNING(f'VAPID_PUBLIC_KEY={public_key}'))
        self.stdout.write(self.style.WARNING(f'VAPID_PRIVATE_KEY={private_pem}'))
        self.stdout.write(self.style.WARNING('VAPID_CLAIMS_EMAIL=admin@finai.app\n'))
