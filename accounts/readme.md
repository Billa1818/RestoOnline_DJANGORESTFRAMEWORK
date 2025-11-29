# 📡 Guide Complet des Endpoints API

## 🔐 AUTHENTIFICATION

### 1. Connexion (Login)
```http
POST /api/accounts/users/login/
Content-Type: application/json

{
  "username": "manager01",
  "password": "MotDePasse123!"
}
```

**Réponse (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "manager01",
    "email": "manager@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "user_type": "manager",
    "phone": "+22997123456",
    "is_available": true,
    "profile_picture": null,
    "total_deliveries": 0,
    "average_rating": "0.00"
  }
}
```

---

### 2. Profil utilisateur connecté
```http
GET /api/accounts/users/me/
Authorization: Bearer {access_token}
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "username": "manager01",
  "email": "manager@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "user_type": "manager",
  "phone": "+22997123456",
  "is_available": true,
  "profile_picture": null,
  "total_deliveries": 0,
  "average_rating": "0.00",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## 🔑 RÉINITIALISATION DE MOT DE PASSE

### 3. Demander la réinitialisation
```http
POST /api/accounts/users/password_reset_request/
Content-Type: application/json

{
  "email": "manager@example.com"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation."
}
```

---

### 4. Confirmer la réinitialisation (avec token)
```http
POST /api/accounts/users/password_reset_confirm/
Content-Type: application/json

{
  "uid": "MQ",
  "token": "c6w7w7-58d45e1234abcdef567890",
  "new_password": "NouveauMotDePasse123!",
  "confirm_password": "NouveauMotDePasse123!"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Votre mot de passe a été réinitialisé avec succès."
}
```

**Erreur (400 Bad Request):**
```json
{
  "error": "Lien de réinitialisation expiré ou invalide"
}
```

---

### 5. Changer le mot de passe (utilisateur connecté)
```http
POST /api/accounts/users/change_password/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "AncienMotDePasse123!",
  "new_password": "NouveauMotDePasse123!",
  "confirm_password": "NouveauMotDePasse123!"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Mot de passe modifié avec succès"
}
```

**Erreur (400 Bad Request):**
```json
{
  "error": "Mot de passe actuel incorrect"
}
```

---

## 👥 GESTION DES UTILISATEURS

### 6. Liste des utilisateurs
```http
GET /api/accounts/users/
Authorization: Bearer {access_token}

# Avec filtrage par type
GET /api/accounts/users/?user_type=delivery
GET /api/accounts/users/?user_type=manager
GET /api/accounts/users/?user_type=admin
```

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "username": "manager01",
    "first_name": "Jean",
    "last_name": "Dupont",
    "user_type": "manager",
    "phone": "+22997123456",
    "is_available": true,
    "average_rating": "0.00"
  },
  {
    "id": 2,
    "username": "livreur01",
    "first_name": "Marie",
    "last_name": "Martin",
    "user_type": "delivery",
    "phone": "+22997654321",
    "is_available": true,
    "average_rating": "4.85"
  }
]
```

---

### 7. Créer un utilisateur
```http
POST /api/accounts/users/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "livreur03",
  "email": "livreur03@example.com",
  "first_name": "Ahmed",
  "last_name": "Ben Ali",
  "user_type": "delivery",
  "phone": "+22997777888",
  "password": "MotDePasse123!",
  "confirm_password": "MotDePasse123!"
}
```

**Réponse (201 Created):**
```json
{
  "id": 5,
  "username": "livreur03",
  "email": "livreur03@example.com",
  "first_name": "Ahmed",
  "last_name": "Ben Ali",
  "user_type": "delivery",
  "phone": "+22997777888",
  "is_available": true,
  "profile_picture": null,
  "total_deliveries": 0,
  "average_rating": "0.00",
  "created_at": "2025-01-15T15:30:00Z",
  "updated_at": "2025-01-15T15:30:00Z"
}
```

---

### 8. Détails d'un utilisateur
```http
GET /api/accounts/users/5/
Authorization: Bearer {access_token}
```

---

### 9. Modifier un utilisateur (complet)
```http
PUT /api/accounts/users/5/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "livreur03",
  "email": "livreur03@example.com",
  "first_name": "Ahmed",
  "last_name": "Ben Ali",
  "user_type": "delivery",
  "phone": "+22997777999",
  "is_available": true
}
```

---

### 10. Modifier un utilisateur (partiel)
```http
PATCH /api/accounts/users/5/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "phone": "+22997777999",
  "is_available": false
}
```

---

### 11. Supprimer un utilisateur
```http
DELETE /api/accounts/users/5/
Authorization: Bearer {access_token}
```

**Réponse (204 No Content)**

---

## 🚴 LIVREURS

### 12. Basculer la disponibilité d'un livreur
```http
POST /api/accounts/users/5/toggle_availability/
Authorization: Bearer {access_token}
```

**Réponse (200 OK):**
```json
{
  "is_available": false
}
```

---

### 13. Liste de tous les livreurs
```http
GET /api/accounts/delivery-persons/
Authorization: Bearer {access_token}
```

**Réponse (200 OK):**
```json
[
  {
    "id": 2,
    "username": "livreur01",
    "first_name": "Marie",
    "last_name": "Martin",
    "phone": "+22997654321",
    "is_available": true,
    "profile_picture": null,
    "total_deliveries": 45,
    "average_rating": "4.85"
  },
  {
    "id": 3,
    "username": "livreur02",
    "first_name": "Paul",
    "last_name": "Dubois",
    "phone": "+22997111222",
    "is_available": false,
    "profile_picture": null,
    "total_deliveries": 32,
    "average_rating": "4.60"
  }
]
```

---

### 14. Liste des livreurs disponibles
```http
GET /api/accounts/delivery-persons/available/
Authorization: Bearer {access_token}
```

**Réponse (200 OK):**
```json
[
  {
    "id": 2,
    "username": "livreur01",
    "first_name": "Marie",
    "last_name": "Martin",
    "phone": "+22997654321",
    "is_available": true,
    "profile_picture": null,
    "total_deliveries": 45,
    "average_rating": "4.85"
  }
]
```

---

### 15. Détails d'un livreur
```http
GET /api/accounts/delivery-persons/2/
Authorization: Bearer {access_token}
```

---

### 16. Statistiques détaillées d'un livreur
```http
GET /api/accounts/delivery-persons/2/statistics/
Authorization: Bearer {access_token}
```

**Réponse (200 OK):**
```json
{
  "total_deliveries": 45,
  "average_rating": 4.85,
  "completed_deliveries": 43,
  "refused_deliveries": 2,
  "total_ratings": 40,
  "ratings_breakdown": {
    "5_stars": 30,
    "4_stars": 8,
    "3_stars": 2,
    "2_stars": 0,
    "1_star": 0
  }
}
```

---

## 📱 APPAREILS CLIENTS (Device-Based Auth)

### 17. Enregistrer un appareil
```http
POST /api/accounts/devices/register/
Content-Type: application/json

{
  "device_id": "abc123xyz789",
  "device_info": {
    "model": "iPhone 14 Pro",
    "os": "iOS 16.5",
    "app_version": "1.0.0"
  },
  "device_name": "iPhone de Jean",
  "fcm_token": "firebase_token_here",
  "customer_name": "Jean Dupont",
  "customer_phone": "+22997123456",
  "customer_email": "jean@example.com"
}
```

**Réponse (201 Created si nouveau, 200 OK si existant):**
```json
{
  "device": {
    "id": 1,
    "device_id": "abc123xyz789",
    "device_info": {
      "model": "iPhone 14 Pro",
      "os": "iOS 16.5",
      "app_version": "1.0.0"
    },
    "device_name": "iPhone de Jean",
    "fcm_token": "firebase_token_here",
    "customer_name": "Jean Dupont",
    "customer_phone": "+22997123456",
    "customer_email": "jean@example.com",
    "first_seen": "2025-01-15T10:00:00Z",
    "last_seen": "2025-01-15T10:00:00Z",
    "is_active": true,
    "is_blocked": false,
    "order_count": 0
  },
  "is_new": true
}
```

---

### 18. Liste des appareils
```http
GET /api/accounts/devices/
```

---

### 19. Détails d'un appareil
```http
GET /api/accounts/devices/abc123xyz789/
```

---

### 20. Mettre à jour les informations client
```http
PATCH /api/accounts/devices/abc123xyz789/update-info/
Content-Type: application/json

{
  "customer_name": "Jean Pierre Dupont",
  "customer_phone": "+22997123457",
  "customer_email": "jeanpierre@example.com"
}
```

---

### 21. Historique des commandes d'un appareil
```http
GET /api/accounts/devices/abc123xyz789/orders/
```

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "order_number": "ORD-20250115-001",
    "status": "delivered",
    "total_amount": "15000.00",
    "created_at": "2025-01-15T12:00:00Z"
  },
  {
    "id": 2,
    "order_number": "ORD-20250115-015",
    "status": "pending",
    "total_amount": "8500.00",
    "created_at": "2025-01-15T14:30:00Z"
  }
]
```

---

### 22. Modifier un appareil
```http
PATCH /api/accounts/devices/abc123xyz789/
Content-Type: application/json

{
  "device_name": "Nouveau nom",
  "fcm_token": "nouveau_token"
}
```

---

### 23. Supprimer un appareil
```http
DELETE /api/accounts/devices/abc123xyz789/
```

---

## 🔄 AUTHENTIFICATION JWT (Token Refresh)

### 24. Rafraîchir le token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Réponse (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 📝 NOTES IMPORTANTES

### Headers requis pour les endpoints authentifiés :
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Permissions :
- 🔓 **AllowAny** : login, password_reset_request, password_reset_confirm, devices/register
- 🔒 **IsAuthenticated** : tous les autres endpoints

### Codes de statut HTTP :
- `200 OK` - Succès
- `201 Created` - Création réussie
- `204 No Content` - Suppression réussie
- `400 Bad Request` - Données invalides
- `401 Unauthorized` - Non authentifié
- `403 Forbidden` - Permissions insuffisantes
- `404 Not Found` - Ressource introuvable
- `500 Internal Server Error` - Erreur serveur

### Types d'utilisateurs :
- `admin` - Administrateur
- `manager` - Gestionnaire
- `delivery` - Livreur