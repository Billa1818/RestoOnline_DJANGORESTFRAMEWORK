# Documentation API - Module Orders

## Vue d'ensemble

---

## Endpoints

### 1. Commandes

**Base URL:** `/api/orders/orders/`

#### 1.1 Lister les commandes

**GET** `/api/orders/orders/`

Récupère la liste des commandes avec filtres optionnels.

**Permissions:** Authentification requise

**Query Parameters:**
- `status` (string, optionnel) : Filtrer par statut
- `device_id` (string, optionnel) : Filtrer par ID d'appareil
- `delivery_person_id` (integer, optionnel) : Filtrer par ID du livreur

**Exemples:**
- `/api/orders/orders/?status=pending`
- `/api/orders/orders/?device_id=abc123xyz`
- `/api/orders/orders/?delivery_person_id=5`

**Réponse 200:**
```json
[
  {
    "id": 1,
    "order_number": "ORD-A1B2C3D4",
    "customer_name": "Marie Kouassi",
    "customer_phone": "+22997654321",
    "status": "preparing",
    "status_display": "En préparation",
    "total": "8500.00",
    "items_count": 3,
    "created_at": "2024-03-15T14:30:00Z",
    "delivered_at": null
  },
  {
    "id": 2,
    "order_number": "ORD-E5F6G7H8",
    "customer_name": "Jean Mensah",
    "customer_phone": "+22997123456",
    "status": "delivered",
    "status_display": "Livrée",
    "total": "12500.00",
    "items_count": 5,
    "created_at": "2024-03-15T12:00:00Z",
    "delivered_at": "2024-03-15T13:45:00Z"
  }
]
```

---

#### 1.2 Créer une commande

**POST** `/api/orders/orders/`

Crée une nouvelle commande.

**Permissions:** Accès public (pas d'authentification requise)

**Body:**
```json
{
  "device": 1,
  "delivery_address": "Cotonou, Akpakpa, Rue 123",
  "delivery_latitude": 6.3654200,
  "delivery_longitude": 2.4183800,
  "delivery_description": "Maison bleue à côté de la pharmacie",
  "customer_name": "Marie Kouassi",
  "customer_phone": "+22997654321",
  "customer_email": "marie.kouassi@email.com",
  "delivery_fee": "500.00",
  "notes": "Livraison urgente SVP",
  "items": [
    {
      "size_id": 15,
      "quantity": 2,
      "special_instructions": "Peu épicé"
    },
    {
      "size_id": 23,
      "quantity": 1,
      "special_instructions": ""
    }
  ]
}
```

**Validations:**
- La commande doit contenir au moins un article
- Chaque `size_id` doit correspondre à un format de plat disponible

**Comportement:**
- Un numéro de commande unique est généré automatiquement (`ORD-XXXXXXXX`)
- Le sous-total et le total sont calculés automatiquement
- Les informations des plats (nom, prix) sont enregistrées au moment de la commande

**Réponse 201:**
```json
{
  "id": 1,
  "order_number": "ORD-A1B2C3D4",
  "device": 1,
  "device_info": {
    "id": 1,
    "device_id": "abc123xyz",
    "device_type": "android",
    "last_active": "2024-03-15T14:30:00Z"
  },
  "delivery_address": "Cotonou, Akpakpa, Rue 123",
  "delivery_latitude": "6.36542000",
  "delivery_longitude": "2.41838000",
  "delivery_description": "Maison bleue à côté de la pharmacie",
  "customer_name": "Marie Kouassi",
  "customer_phone": "+22997654321",
  "customer_email": "marie.kouassi@email.com",
  "status": "pending",
  "status_display": "En attente",
  "manager": null,
  "manager_info": null,
  "delivery_person": null,
  "delivery_person_info": null,
  "subtotal": "8000.00",
  "delivery_fee": "500.00",
  "total": "8500.00",
  "notes": "Livraison urgente SVP",
  "cancellation_reason": "",
  "refusal_reason": "",
  "items": [
    {
      "id": 1,
      "menu_item": 5,
      "size": 15,
      "menu_item_details": {
        "id": 5,
        "name": "Poulet Yassa",
        "slug": "poulet-yassa",
        "image": "/media/menu_items/poulet-yassa.jpg",
        "category_name": "Plats principaux"
      },
      "size_details": {
        "id": 15,
        "size": "small",
        "size_display": "Petit",
        "price": "2500.00"
      },
      "item_name": "Poulet Yassa",
      "size_name": "Petit",
      "item_price": "2500.00",
      "quantity": 2,
      "subtotal": "5000.00",
      "special_instructions": "Peu épicé",
      "created_at": "2024-03-15T14:30:00Z"
    },
    {
      "id": 2,
      "menu_item": 8,
      "size": 23,
      "menu_item_details": {
        "id": 8,
        "name": "Jus d'Orange",
        "slug": "jus-orange",
        "image": "/media/menu_items/jus-orange.jpg",
        "category_name": "Boissons"
      },
      "size_details": {
        "id": 23,
        "size": "large",
        "size_display": "Grand",
        "price": "3000.00"
      },
      "item_name": "Jus d'Orange",
      "size_name": "Grand",
      "item_price": "3000.00",
      "quantity": 1,
      "subtotal": "3000.00",
      "special_instructions": "",
      "created_at": "2024-03-15T14:30:00Z"
    }
  ],
  "created_at": "2024-03-15T14:30:00Z",
  "accepted_at": null,
  "ready_at": null,
  "assigned_at": null,
  "picked_up_at": null,
  "delivered_at": null,
  "updated_at": "2024-03-15T14:30:00Z"
}
```

---

#### 1.3 Détails d'une commande

**GET** `/api/orders/orders/{order_number}/`

Récupère les détails complets d'une commande.

**Permissions:** Authentification requise

**Réponse 200:** Objet commande complet (format identique à 1.2)

---

#### 1.4 Modifier une commande

**PUT/PATCH** `/api/orders/orders/{order_number}/`

Modifie certaines informations d'une commande.

**Permissions:** Authentification requise

**Body (PATCH):**
```json
{
  "delivery_fee": "1000.00",
  "notes": "Nouvelle instruction"
}
```

**Réponse 200:** Objet commande mis à jour

---

#### 1.5 Supprimer une commande

**DELETE** `/api/orders/orders/{order_number}/`

Supprime une commande (action rare, préférer l'annulation).

**Permissions:** Authentification requise

**Réponse 204:** No Content

---

#### 1.6 Commandes en attente

**GET** `/api/orders/orders/pending/`

Récupère toutes les commandes avec le statut `pending`.

**Permissions:** Authentification requise

**Réponse 200:** Liste de commandes (format simplifié comme 1.1)

---

#### 1.7 Commandes actives

**GET** `/api/orders/orders/active/`

Récupère les commandes en cours (statuts: `accepted`, `preparing`, `ready`, `assigned`, `in_delivery`).

**Permissions:** Authentification requise

**Réponse 200:** Liste de commandes actives

---

#### 1.8 Accepter une commande

**POST** `/api/orders/orders/{order_number}/accept/`

Le manager accepte une commande en attente.

**Permissions:** Authentification requise (Manager)

**Body:** Vide

**Validations:**
- Le statut doit être `pending`

**Comportement:**
- Le statut passe à `accepted`
- Le manager est enregistré
- La date d'acceptation est enregistrée

**Réponse 200:**
```json
{
  "id": 1,
  "status": "accepted",
  "status_display": "Acceptée",
  "manager": 2,
  "manager_info": {
    "id": 2,
    "username": "manager1",
    "name": "Admin Manager"
  },
  "accepted_at": "2024-03-15T14:35:00Z",
  ...
}
```

---

#### 1.9 Refuser une commande

**POST** `/api/orders/orders/{order_number}/refuse/`

Le manager refuse une commande en attente.

**Permissions:** Authentification requise (Manager)

**Body:**
```json
{
  "reason": "Ingrédients indisponibles"
}
```

**Validations:**
- Le statut doit être `pending`

**Réponse 200:**
```json
{
  "id": 1,
  "status": "refused",
  "status_display": "Refusée",
  "refusal_reason": "Ingrédients indisponibles",
  ...
}
```

---

#### 1.10 Démarrer la préparation

**POST** `/api/orders/orders/{order_number}/start_preparing/`

Marque qu'une commande est en cours de préparation.

**Permissions:** Authentification requise

**Body:** Vide

**Validations:**
- Le statut doit être `accepted`

**Réponse 200:**
```json
{
  "status": "preparing"
}
```

---

#### 1.11 Marquer comme prête

**POST** `/api/orders/orders/{order_number}/mark_ready/`

Marque qu'une commande est prête pour la livraison.

**Permissions:** Authentification requise

**Body:** Vide

**Validations:**
- Le statut doit être `preparing`

**Comportement:**
- Le statut passe à `ready`
- La date de préparation terminée est enregistrée

**Réponse 200:**
```json
{
  "status": "ready"
}
```

---

#### 1.12 Annuler une commande

**POST** `/api/orders/orders/{order_number}/cancel/`

Annule une commande (Client ou Manager).

**Permissions:** Authentification requise (ou accès public si nécessaire)

**Body:**
```json
{
  "reason": "Changement de plans"
}
```

**Validations:**
- Les commandes `delivered` ou déjà `cancelled` ne peuvent pas être annulées

**Réponse 200:**
```json
{
  "status": "cancelled"
}
```

---

#### 1.13 Suivre une commande

**GET** `/api/orders/orders/{order_number}/track/`

Permet de suivre une commande en temps réel (endpoint public).

**Permissions:** Accès public

**Réponse 200:**
```json
{
  "id": 1,
  "order_number": "ORD-A1B2C3D4",
  "customer_name": "Marie Kouassi",
  "status": "in_delivery",
  "status_display": "En cours de livraison",
  "delivery_person_info": {
    "id": 5,
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+22997123456",
    "vehicle_type": "moto"
  },
  "delivery_location": {
    "latitude": 6.3654200,
    "longitude": 2.4183800,
    "timestamp": "2024-03-15T15:30:00Z"
  },
  "items": [...],
  ...
}
```

**Note:** La position du livreur est incluse uniquement si le statut est `in_delivery` et qu'une affectation existe.

---

#### 1.14 Statistiques des commandes

**GET** `/api/orders/orders/statistics/`

Récupère les statistiques globales des commandes.

**Permissions:** Authentification requise

**Réponse 200:**
```json
{
  "total": 245,
  "pending": 8,
  "active": 15,
  "delivered": 210,
  "cancelled": 10,
  "refused": 2
}
```

---

### 2. Paniers

**Base URL:** `/api/orders/carts/`

#### 2.1 Lister les paniers

**GET** `/api/orders/carts/`

Récupère la liste des paniers.

**Permissions:** Accès public

**Query Parameters:**
- `device_id` (string, optionnel) : Filtrer par ID d'appareil

**Réponse 200:**
```json
[
  {
    "id": 1,
    "device": 1,
    "items": [...],
    "total_items": 5,
    "total_amount": "12500.00",
    "created_at": "2024-03-15T10:00:00Z",
    "updated_at": "2024-03-15T14:30:00Z"
  }
]
```

---

#### 2.2 Mon panier

**GET/POST** `/api/orders/carts/my_cart/`

Obtient ou crée le panier d'un appareil.

**Permissions:** Accès public

**Query Parameters (GET):**
- `device_id` (string, requis)

**Body (POST):**
```json
{
  "device_id": "abc123xyz"
}
```

**Comportement:**
- Si l'appareil n'existe pas, il est créé automatiquement
- Si le panier n'existe pas, il est créé automatiquement

**Réponse 200:**
```json
{
  "id": 1,
  "device": 1,
  "items": [
    {
      "id": 1,
      "menu_item": 5,
      "size": 15,
      "menu_item_details": {
        "id": 5,
        "name": "Poulet Yassa",
        "slug": "poulet-yassa",
        "image": "/media/menu_items/poulet-yassa.jpg",
        "category_name": "Plats principaux",
        "is_available": true,
        "min_price": "2500.00",
        "max_price": "4500.00"
      },
      "size_details": {
        "id": 15,
        "size": "small",
        "size_display": "Petit",
        "price": "2500.00",
        "is_available": true,
        "portion_description": "Portion individuelle"
      },
      "quantity": 2,
      "special_instructions": "Peu épicé",
      "item_total": "5000.00",
      "added_at": "2024-03-15T13:00:00Z",
      "updated_at": "2024-03-15T13:15:00Z"
    },
    {
      "id": 2,
      "menu_item": 8,
      "size": 23,
      "menu_item_details": {
        "id": 8,
        "name": "Jus d'Orange",
        "slug": "jus-orange",
        "image": "/media/menu_items/jus-orange.jpg",
        "category_name": "Boissons",
        "is_available": true,
        "min_price": "1500.00",
        "max_price": "3000.00"
      },
      "size_details": {
        "id": 23,
        "size": "large",
        "size_display": "Grand",
        "price": "3000.00",
        "is_available": true,
        "portion_description": "1L"
      },
      "quantity": 1,
      "special_instructions": "",
      "item_total": "3000.00",
      "added_at": "2024-03-15T13:10:00Z",
      "updated_at": "2024-03-15T13:10:00Z"
    }
  ],
  "total_items": 3,
  "total_amount": "8000.00",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-15T13:15:00Z"
}
```

---

#### 2.3 Ajouter un article

**POST** `/api/orders/carts/{id}/add_item/`

Ajoute un article au panier ou incrémente la quantité s'il existe déjà.

**Permissions:** Accès public

**Body:**
```json
{
  "menu_item_id": 5,
  "size_id": 15,
  "quantity": 2,
  "special_instructions": "Peu épicé"
}
```

**Validations:**
- Le plat et le format doivent être disponibles (`is_available=True`)
- Le format doit appartenir au plat spécifié

**Comportement:**
- Si l'article (même plat + même format) existe déjà, la quantité est incrémentée
- Sinon, un nouvel article est créé

**Réponse 200:** Panier complet mis à jour (format identique à 2.2)

---

#### 2.4 Mettre à jour un article

**POST** `/api/orders/carts/{id}/update_item/`

Modifie la quantité d'un article dans le panier.

**Permissions:** Accès public

**Body:**
```json
{
  "item_id": 1,
  "quantity": 3
}
```

**Comportement:**
- Si `quantity > 0`: la quantité est mise à jour
- Si `quantity <= 0`: l'article est supprimé du panier

**Réponse 200:** Panier complet mis à jour

---

#### 2.5 Retirer un article

**POST** `/api/orders/carts/{id}/remove_item/`

Supprime un article du panier.

**Permissions:** Accès public

**Body:**
```json
{
  "item_id": 1
}
```

**Réponse 200:** Panier complet mis à jour

---

#### 2.6 Vider le panier

**POST** `/api/orders/carts/{id}/clear/`

Supprime tous les articles du panier.

**Permissions:** Accès public

**Body:** Vide

**Réponse 200:**
```json
{
  "id": 1,
  "device": 1,
  "items": [],
  "total_items": 0,
  "total_amount": "0.00",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-15T14:45:00Z"
}
```

---

#### 2.7 Checkout (Transformer en commande)

**POST** `/api/orders/carts/{id}/checkout/`

Transforme le contenu du panier en une commande officielle.

**Permissions:** Accès public

**Body:**
```json
{
  "delivery_address": "Cotonou, Akpakpa, Rue 123",
  "delivery_latitude": 6.3654200,
  "delivery_longitude": 2.4183800,
  "delivery_description": "Maison bleue à côté de la pharmacie",
  "customer_name": "Marie Kouassi",
  "customer_phone": "+22997654321",
  "customer_email": "marie.kouassi@email.com",
  "delivery_fee": "500.00",
  "notes": "Livraison urgente SVP"
}
```

**Validations:**
- Le panier ne doit pas être vide

**Comportement:**
1. Crée une nouvelle commande avec tous les articles du panier
2. Vide automatiquement le panier après création
3. Génère un numéro de commande unique

**Réponse 201:** Commande complète créée (format identique à 1.2)

**Erreur 400:**
```json
{
  "error": "Le panier est vide"
}
```

---

## Flux de travail typique

### Pour un Client:

1. **Ajouter au panier:**
   - Obtenir/créer son panier: `GET /api/orders/carts/my_cart/?device_id=abc123`
   - Ajouter des articles: `POST /api/orders/carts/{id}/add_item/`
   - Modifier quantités: `POST /api/orders/carts/{id}/update_item/`

2. **Commander:**
   - Finaliser: `POST /api/orders/carts/{id}/checkout/`
   - Suivre la commande: `GET /api/orders/orders/{order_number}/track/`

### Pour un Manager:

1. **Gérer les nouvelles commandes:**
   - Voir les commandes en attente: `GET /api/orders/orders/pending/`
   - Accepter: `POST /api/orders/orders/{order_number}/accept/`
   - Ou refuser: `POST /api/orders/orders/{order_number}/refuse/`

2. **Préparer les commandes:**
   - Démarrer: `POST /api/orders/orders/{order_number}/start_preparing/`
   - Marquer prête: `POST /api/orders/orders/{order_number}/mark_ready/`

3. **Suivre les statistiques:**
   - `GET /api/orders/orders/statistics/`
   - `GET /api/orders/orders/active/`

---

## Statuts des commandes

| Statut | Description | Actions possibles |
|--------|-------------|-------------------|
| `pending` | En attente de validation | Accepter, Refuser, Annuler |
| `accepted` | Acceptée par le manager | Démarrer préparation, Annuler |
| `preparing` | En cours de préparation | Marquer prête, Annuler |
| `ready` | Prête pour livraison | Assigner à un livreur (via module delivery) |
| `assigned` | Assignée à un livreur | Géré par le module delivery |
| `in_delivery` | En cours de livraison | Géré par le module delivery |
| `delivered` | Livrée au client | Aucune (terminal) |
| `cancelled` | Annulée | Aucune (terminal) |
| `refused` | Refusée par le restaurant | Aucune (terminal) |

---

## Calculs automatiques

### Sous-total et Total
```
Sous-total = Σ (prix_format × quantité) pour chaque article
Total = Sous-total + Frais de livraison
```

### Total du panier
```
Total articles = Σ quantité pour chaque article
Montant total = Σ (prix_format × quantité) pour chaque article
```

---

## Gestion des appareils (ClientDevice)

Le système utilise un `device_id` unique pour identifier chaque appareil client (mobile, web). Cet ID permet de:
- Maintenir un panier persistant par appareil
- Associer les commandes à l'appareil utilisé
- Suivre l'historique des commandes par appareil

**Recommandation:** Générer un UUID côté client lors de la première utilisation de l'application.

---

## Intégration avec d'autres modules

### Module Menu
- Validation de disponibilité des plats et formats
- Récupération des prix actuels
- Enregistrement des informations au moment de la commande (snapshot)

### Module Delivery
- Une commande `ready` peut être assignée à un livreur
- Le suivi en temps réel inclut la position du livreur si disponible

### Module Ratings
- Les commandes `delivered` peuvent être notées par le client

---

## Codes d'erreur communs

- `400 Bad Request`: Données invalides, panier vide, action non autorisée
- `401 Unauthorized`: Non authentifié (endpoints protégés)
- `404 Not Found`: Commande ou article introuvable
- `422 Unprocessable Entity`: Validation échouée

---

## Notes importantes

1. **Snapshot des prix:** Les prix des articles sont enregistrés au moment de la commande pour éviter les modifications ultérieures

2. **Calculs automatiques:** Le système recalcule automatiquement les sous-totaux et totaux - ne pas les fournir manuellement

3. **Numéro de commande:** Généré automatiquement au format `ORD-XXXXXXXX` (8 caractères hexadécimaux)

4. **Panier persistant:** Un panier reste actif tant qu'il n'est pas vidé ou transformé en commande

5. **Tracking public:** L'endpoint `/track/` est accessible sans authentification pour permettre le suivi par lien direct