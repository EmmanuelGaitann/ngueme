from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, HttpResponse
import os


def service_worker(request):
    """Sert le service worker depuis /sw.js avec le header scope complet."""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


urlpatterns = [
    path('admin/',     admin.site.urls),
    path('sw.js',      service_worker, name='sw'),
    path('',           include('apps.dashboard.urls')),
    path('auth/',      include('apps.accounts.urls')),
    path('journal/',   include('apps.transactions.urls')),
    path('ia/',        include('apps.ai_advisor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personnalisation admin
admin.site.site_header  = 'FIN.AI Administration'
admin.site.site_title   = 'FIN.AI'
admin.site.index_title  = 'Tableau de bord administration'
