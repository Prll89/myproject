from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home, dashboard
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Incluye las rutas de la aplicación 'accounts'
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),  # Redirige la raíz a login
    path('dashboard/', dashboard, name='dashboard'),
]

# Añadir esta línea al final del archivo para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

