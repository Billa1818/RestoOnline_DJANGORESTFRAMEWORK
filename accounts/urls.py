# ===================================
# accounts/urls.py
# ===================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DeliveryPersonViewSet, ClientDeviceViewSet

# Configuration du router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'delivery-persons', DeliveryPersonViewSet, basename='delivery-person')
router.register(r'devices', ClientDeviceViewSet, basename='device')

app_name = 'accounts'

urlpatterns = [
    # Routes du router (génère automatiquement les routes CRUD et les actions)
    path('', include(router.urls)),
]

"""
Routes générées automatiquement par le router :

AUTHENTIFICATION:
- POST   /api/accounts/users/login/                      - Connexion
- GET    /api/accounts/users/me/                         - Profil utilisateur connecté
- POST   /api/accounts/users/password_reset_request/     - Demande réinitialisation
- POST   /api/accounts/users/password_reset_confirm/     - Confirmer réinitialisation
- POST   /api/accounts/users/change_password/            - Changer mot de passe

GESTION UTILISATEURS (CRUD):
- GET    /api/accounts/users/                            - Liste des utilisateurs
- POST   /api/accounts/users/                            - Créer un utilisateur
- GET    /api/accounts/users/{id}/                       - Détails d'un utilisateur
- PUT    /api/accounts/users/{id}/                       - Modifier un utilisateur (complet)
- PATCH  /api/accounts/users/{id}/                       - Modifier un utilisateur (partiel)
- DELETE /api/accounts/users/{id}/                       - Supprimer un utilisateur

LIVREURS:
- POST   /api/accounts/users/{id}/toggle_availability/   - Basculer disponibilité livreur
- GET    /api/accounts/delivery-persons/                 - Liste des livreurs
- GET    /api/accounts/delivery-persons/available/       - Livreurs disponibles
- GET    /api/accounts/delivery-persons/{id}/            - Détails d'un livreur
- GET    /api/accounts/delivery-persons/{id}/statistics/ - Statistiques d'un livreur

APPAREILS CLIENTS:
- GET    /api/accounts/devices/                          - Liste des appareils
- POST   /api/accounts/devices/                          - Créer un appareil
- GET    /api/accounts/devices/{device_id}/              - Détails d'un appareil
- PUT    /api/accounts/devices/{device_id}/              - Modifier un appareil
- PATCH  /api/accounts/devices/{device_id}/              - Modifier un appareil (partiel)
- DELETE /api/accounts/devices/{device_id}/              - Supprimer un appareil
- POST   /api/accounts/devices/register/                 - Enregistrer un appareil
- PATCH  /api/accounts/devices/{device_id}/update-info/  - Mettre à jour infos client
- GET    /api/accounts/devices/{device_id}/orders/       - Commandes d'un appareil
"""


# ===================================
# Projet principal urls.py
# ===================================

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/delivery/', include('delivery.urls')),
    path('api/ratings/', include('ratings.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # JWT Authentication (si vous utilisez simplejwt)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""