# Documentation des Endpoints - Application Ratings

## Vue d'ensemble
Cette application gère les évaluations et notes des livraisons et des plats du menu par les clients.

---

## Endpoints - Notes de Livraison (Delivery Ratings)

### 1. Lister les notes de livraison
```
GET /api/delivery-ratings/
```

**Permissions:** Authentification requise

**Paramètres de requête (optionnels):**
- `delivery_person_id` - Filtrer par ID du livreur
- `device_id` - Filtrer par ID de l'appareil
- `order_id` - Filtrer par ID de commande

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "order": 5,
    "order_number": "CMD-2024-001",
    "device": 3,
    "delivery_person": 10,
    "delivery_person_details": {
      "id": 10,
      "first_name": "Jean",
      "last_name": "Dupont",
      "phone_number": "+22997000000",
      "average_rating": 4.5,
      "is_available": true
    },
    "customer_name": "Alice Martin",
    "rating": 5,
    "comment": "Livraison rapide et livreur très professionnel",
    "speed_rating": 5,
    "professionalism_rating": 5,
    "created_at": "2024-11-27T10:30:00Z",
    "updated_at": "2024-11-27T10:30:00Z"
  }
]
```

---

### 2. Créer une note de livraison
```
POST /api/delivery-ratings/
```

**Permissions:** Accès public (AllowAny)

**Corps de la requête:**
```json
{
  "order": 5,
  "device": 3,
  "delivery_person": 10,
  "rating": 5,
  "comment": "Excellent service",
  "speed_rating": 5,
  "professionalism_rating": 4
}
```

**Champs:**
- `order` (integer, requis) - ID de la commande
- `device` (integer, requis) - ID de l'appareil client
- `delivery_person` (integer, requis) - ID du livreur
- `rating` (integer, requis) - Note globale (1-5)
- `comment` (string, optionnel) - Commentaire
- `speed_rating` (integer, optionnel) - Note de rapidité (1-5)
- `professionalism_rating` (integer, optionnel) - Note de professionnalisme (1-5)

**Réponse succès (201 Created):**
```json
{
  "id": 1,
  "order": 5,
  "order_number": "CMD-2024-001",
  "device": 3,
  "delivery_person": 10,
  "delivery_person_details": {
    "id": 10,
    "first_name": "Jean",
    "last_name": "Dupont",
    "average_rating": 4.7
  },
  "customer_name": "Alice Martin",
  "rating": 5,
  "comment": "Excellent service",
  "speed_rating": 5,
  "professionalism_rating": 4,
  "created_at": "2024-11-27T10:30:00Z",
  "updated_at": "2024-11-27T10:30:00Z"
}
```

**Réponse erreur (404 Not Found):**
```json
{
  "error": "Commande non trouvée"
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "Seules les commandes livrées peuvent être notées"
}
```

ou

```json
{
  "error": "Cette livraison a déjà été notée"
}
```

**Actions automatiques:**
- Met à jour le champ `average_rating` du livreur

---

### 3. Détails d'une note de livraison
```
GET /api/delivery-ratings/{id}/
```

**Permissions:** Authentification requise

**Réponse (200 OK):**
```json
{
  "id": 1,
  "order": 5,
  "order_number": "CMD-2024-001",
  "delivery_person": 10,
  "delivery_person_details": {...},
  "rating": 5,
  "comment": "Excellent service",
  "speed_rating": 5,
  "professionalism_rating": 4,
  "created_at": "2024-11-27T10:30:00Z"
}
```

---

### 4. Modifier une note de livraison
```
PUT /api/delivery-ratings/{id}/
PATCH /api/delivery-ratings/{id}/
```

**Permissions:** Authentification requise

**Corps de la requête (PATCH - partiel):**
```json
{
  "rating": 4,
  "comment": "Bon service mais un peu lent"
}
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "rating": 4,
  "comment": "Bon service mais un peu lent",
  "updated_at": "2024-11-27T11:00:00Z"
}
```

---

### 5. Supprimer une note de livraison
```
DELETE /api/delivery-ratings/{id}/
```

**Permissions:** Authentification requise

**Réponse (204 No Content)**

---

### 6. Notes par livreur
```
GET /api/delivery-ratings/by_delivery_person/?delivery_person_id={id}
```

**Permissions:** Authentification requise

**Paramètres de requête:**
- `delivery_person_id` (requis) - ID du livreur

**Réponse (200 OK):**
```json
{
  "average_rating": 4.5,
  "total_ratings": 120,
  "distribution": {
    "5_stars": 80,
    "4_stars": 30,
    "3_stars": 7,
    "2_stars": 2,
    "1_star": 1
  },
  "ratings": [
    {
      "id": 1,
      "order_number": "CMD-2024-001",
      "rating": 5,
      "comment": "Excellent",
      "speed_rating": 5,
      "professionalism_rating": 5,
      "created_at": "2024-11-27T10:30:00Z"
    }
  ]
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "delivery_person_id requis"
}
```

---

## Endpoints - Notes de Plats (Menu Item Ratings)

### 7. Lister les notes de plats
```
GET /api/menu-item-ratings/
```

**Permissions:** Authentification requise

**Paramètres de requête (optionnels):**
- `menu_item_id` - Filtrer par ID du plat
- `device_id` - Filtrer par ID de l'appareil
- `order_id` - Filtrer par ID de commande

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "order_item": 15,
    "order": 5,
    "order_number": "CMD-2024-001",
    "device": 3,
    "menu_item": 8,
    "menu_item_details": {
      "id": 8,
      "name": "Poulet Yassa",
      "description": "Poulet mariné au citron",
      "price": "3500.00",
      "image": "https://example.com/poulet-yassa.jpg",
      "average_rating": 4.7,
      "total_ratings": 85
    },
    "customer_name": "Alice Martin",
    "rating": 5,
    "comment": "Délicieux, très bien présenté",
    "taste_rating": 5,
    "presentation_rating": 5,
    "portion_rating": 4,
    "created_at": "2024-11-27T10:35:00Z",
    "updated_at": "2024-11-27T10:35:00Z"
  }
]
```

---

### 8. Créer une note de plat
```
POST /api/menu-item-ratings/
```

**Permissions:** Accès public (AllowAny)

**Corps de la requête:**
```json
{
  "order_item": 15,
  "order": 5,
  "device": 3,
  "menu_item": 8,
  "rating": 5,
  "comment": "Délicieux!",
  "taste_rating": 5,
  "presentation_rating": 5,
  "portion_rating": 4
}
```

**Champs:**
- `order_item` (integer, requis) - ID de l'article de commande
- `order` (integer, requis) - ID de la commande
- `device` (integer, requis) - ID de l'appareil client
- `menu_item` (integer, requis) - ID du plat
- `rating` (integer, requis) - Note globale (1-5)
- `comment` (string, optionnel) - Commentaire
- `taste_rating` (integer, optionnel) - Note de goût (1-5)
- `presentation_rating` (integer, optionnel) - Note de présentation (1-5)
- `portion_rating` (integer, optionnel) - Note de portion (1-5)

**Réponse succès (201 Created):**
```json
{
  "id": 1,
  "order_item": 15,
  "order": 5,
  "order_number": "CMD-2024-001",
  "device": 3,
  "menu_item": 8,
  "menu_item_details": {
    "id": 8,
    "name": "Poulet Yassa",
    "average_rating": 4.8,
    "total_ratings": 86
  },
  "rating": 5,
  "comment": "Délicieux!",
  "taste_rating": 5,
  "presentation_rating": 5,
  "portion_rating": 4,
  "created_at": "2024-11-27T10:35:00Z"
}
```

**Réponse erreur (404 Not Found):**
```json
{
  "error": "Commande ou article non trouvé"
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "Seules les commandes livrées peuvent être notées"
}
```

ou

```json
{
  "error": "Cet article a déjà été noté"
}
```

**Actions automatiques:**
- Met à jour les champs `average_rating` et `total_ratings` du plat

---

### 9. Détails d'une note de plat
```
GET /api/menu-item-ratings/{id}/
```

**Permissions:** Authentification requise

**Réponse (200 OK):**
```json
{
  "id": 1,
  "order_item": 15,
  "order": 5,
  "menu_item": 8,
  "menu_item_details": {...},
  "rating": 5,
  "comment": "Délicieux!",
  "taste_rating": 5,
  "presentation_rating": 5,
  "portion_rating": 4,
  "created_at": "2024-11-27T10:35:00Z"
}
```

---

### 10. Modifier une note de plat
```
PUT /api/menu-item-ratings/{id}/
PATCH /api/menu-item-ratings/{id}/
```

**Permissions:** Authentification requise

**Corps de la requête (PATCH - partiel):**
```json
{
  "rating": 4,
  "comment": "Bon mais un peu salé"
}
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "rating": 4,
  "comment": "Bon mais un peu salé",
  "updated_at": "2024-11-27T11:00:00Z"
}
```

---

### 11. Supprimer une note de plat
```
DELETE /api/menu-item-ratings/{id}/
```

**Permissions:** Authentification requise

**Réponse (204 No Content)**

---

### 12. Notes par plat
```
GET /api/menu-item-ratings/by_menu_item/?menu_item_id={id}
```

**Permissions:** Accès public (AllowAny)

**Paramètres de requête:**
- `menu_item_id` (requis) - ID du plat

**Réponse (200 OK):**
```json
{
  "average_rating": 4.7,
  "total_ratings": 85,
  "distribution": {
    "5_stars": 60,
    "4_stars": 20,
    "3_stars": 3,
    "2_stars": 1,
    "1_star": 1
  },
  "criteria_averages": {
    "taste": 4.8,
    "presentation": 4.6,
    "portion": 4.5
  },
  "ratings": [
    {
      "id": 1,
      "order_number": "CMD-2024-001",
      "customer_name": "Alice Martin",
      "rating": 5,
      "comment": "Délicieux!",
      "taste_rating": 5,
      "presentation_rating": 5,
      "portion_rating": 4,
      "created_at": "2024-11-27T10:35:00Z"
    }
  ]
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "menu_item_id requis"
}
```

---

### 13. Noter plusieurs plats en une fois
```
POST /api/menu-item-ratings/rate_order_items/
```

**Permissions:** Authentification requise

**Description:** Permet de noter plusieurs plats d'une même commande en une seule requête.

**Corps de la requête:**
```json
{
  "order_id": 5,
  "items": [
    {
      "order_item": 15,
      "device": 3,
      "menu_item": 8,
      "rating": 5,
      "comment": "Excellent poulet yassa",
      "taste_rating": 5,
      "presentation_rating": 5,
      "portion_rating": 4
    },
    {
      "order_item": 16,
      "device": 3,
      "menu_item": 12,
      "rating": 4,
      "comment": "Bon riz, portion généreuse",
      "taste_rating": 4,
      "presentation_rating": 4,
      "portion_rating": 5
    }
  ]
}
```

**Champs:**
- `order_id` (integer, requis) - ID de la commande
- `items` (array, requis) - Liste des notes à créer
  - Chaque item contient les mêmes champs que la création d'une note simple

**Réponse succès (201 Created):**
```json
{
  "created": [
    {
      "id": 1,
      "order_item": 15,
      "menu_item": 8,
      "rating": 5,
      "comment": "Excellent poulet yassa",
      "created_at": "2024-11-27T10:35:00Z"
    },
    {
      "id": 2,
      "order_item": 16,
      "menu_item": 12,
      "rating": 4,
      "comment": "Bon riz, portion généreuse",
      "created_at": "2024-11-27T10:35:00Z"
    }
  ],
  "errors": []
}
```

**Réponse avec erreurs partielles (201 Created):**
```json
{
  "created": [
    {
      "id": 1,
      "order_item": 15,
      "rating": 5,
      "created_at": "2024-11-27T10:35:00Z"
    }
  ],
  "errors": [
    {
      "order_item_id": 16,
      "errors": {
        "rating": ["Ce champ est requis."]
      }
    }
  ]
}
```

**Réponse erreur (404 Not Found):**
```json
{
  "error": "Commande non trouvée"
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "Seules les commandes livrées peuvent être notées"
}
```

ou

```json
{
  "error": "order_id et items requis"
}
```

---

## Règles de validation

### Notes de livraison
- La commande doit avoir le statut `delivered`
- Une commande ne peut être notée qu'une seule fois
- Les notes doivent être comprises entre 1 et 5
- Le livreur doit avoir le type d'utilisateur `delivery`

### Notes de plats
- La commande doit avoir le statut `delivered`
- Un plat ne peut être noté qu'une seule fois par appareil (device)
- Les notes doivent être comprises entre 1 et 5
- L'article (order_item) doit appartenir à la commande spécifiée

---

## Système de notation

### Échelle de notation
- **5 étoiles** - Excellent
- **4 étoiles** - Très bien
- **3 étoiles** - Bien
- **2 étoiles** - Passable
- **1 étoile** - Mauvais

### Critères de notation des livraisons
- **Note globale** (rating) - Évaluation générale
- **Rapidité** (speed_rating) - Temps de livraison
- **Professionnalisme** (professionalism_rating) - Comportement du livreur

### Critères de notation des plats
- **Note globale** (rating) - Évaluation générale
- **Goût** (taste_rating) - Saveur du plat
- **Présentation** (presentation_rating) - Aspect visuel
- **Portion** (portion_rating) - Quantité servie

---

## Mises à jour automatiques

### Après création d'une note de livraison
- Le champ `average_rating` du livreur est recalculé automatiquement
- La moyenne est calculée sur toutes les notes reçues par le livreur

### Après création d'une note de plat
- Les champs `average_rating` et `total_ratings` du plat sont mis à jour
- Les moyennes sont calculées sur toutes les notes du plat

---

## Cas d'usage typiques

### 1. Client note sa livraison après réception
```
POST /api/delivery-ratings/
{
  "order": 5,
  "device": 3,
  "delivery_person": 10,
  "rating": 5,
  "speed_rating": 5,
  "professionalism_rating": 5
}
```

### 2. Client note tous les plats de sa commande
```
POST /api/menu-item-ratings/rate_order_items/
{
  "order_id": 5,
  "items": [...]
}
```

### 3. Consultation des notes d'un plat avant commande
```
GET /api/menu-item-ratings/by_menu_item/?menu_item_id=8
```

### 4. Consultation du profil d'un livreur
```
GET /api/delivery-ratings/by_delivery_person/?delivery_person_id=10
```

---

## Notes importantes

- **Unicité:** Une livraison = une note, Un plat par commande/appareil = une note
- **Statut requis:** Seules les commandes avec statut `delivered` peuvent être notées
- **Permissions:** La création de notes est publique pour faciliter l'accès aux clients non authentifiés
- **Modifications:** Les notes peuvent être modifiées après création (authentification requise)
- **Statistiques:** Les moyennes et distributions sont calculées en temps réel