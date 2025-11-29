# Documentation API - Module Menu

## Endpoints

### 1. Catégories

**Base URL:** `/api/menu/categories/`

#### 1.1 Lister les catégories

**GET** `/api/menu/categories/`

Récupère la liste des catégories actives (pour les utilisateurs non authentifiés) ou toutes les catégories (pour les utilisateurs authentifiés).

**Permissions:** Accès public pour lecture

**Réponse 200:**
```json
[
  {
    "id": 1,
    "name": "Plats principaux",
    "slug": "plats-principaux",
    "description": "Nos délicieux plats principaux",
    "icon": "/media/categories/plats.jpg",
    "order": 1,
    "is_active": true,
    "items_count": 15,
    "created_at": "2024-03-01T10:00:00Z",
    "updated_at": "2024-03-15T14:30:00Z"
  },
  {
    "id": 2,
    "name": "Boissons",
    "slug": "boissons",
    "description": "Boissons fraîches et chaudes",
    "icon": "/media/categories/boissons.jpg",
    "order": 2,
    "is_active": true,
    "items_count": 8,
    "created_at": "2024-03-01T10:05:00Z",
    "updated_at": "2024-03-10T09:15:00Z"
  }
]
```

---

#### 1.2 Créer une catégorie

**POST** `/api/menu/categories/`

Crée une nouvelle catégorie.

**Permissions:** Authentification requise

**Body:**
```json
{
  "name": "Desserts",
  "slug": "desserts",
  "description": "Nos délicieux desserts maison",
  "icon": "<fichier image>",
  "order": 3,
  "is_active": true
}
```

**Réponse 201:**
```json
{
  "id": 3,
  "name": "Desserts",
  "slug": "desserts",
  "description": "Nos délicieux desserts maison",
  "icon": "/media/categories/desserts.jpg",
  "order": 3,
  "is_active": true,
  "items_count": 0,
  "created_at": "2024-03-15T15:00:00Z",
  "updated_at": "2024-03-15T15:00:00Z"
}
```

---

#### 1.3 Détails d'une catégorie

**GET** `/api/menu/categories/{slug}/`

Récupère les détails d'une catégorie spécifique.

**Permissions:** Accès public

**Réponse 200:** Objet catégorie (format identique à 1.1)

---

#### 1.4 Modifier une catégorie

**PUT/PATCH** `/api/menu/categories/{slug}/`

Modifie une catégorie existante.

**Permissions:** Authentification requise

**Body (PATCH):**
```json
{
  "order": 5,
  "is_active": false
}
```

**Réponse 200:** Objet catégorie mis à jour

---

#### 1.5 Supprimer une catégorie

**DELETE** `/api/menu/categories/{slug}/`

Supprime une catégorie (et tous ses plats associés en cascade).

**Permissions:** Authentification requise

**Réponse 204:** No Content

---

#### 1.6 Plats d'une catégorie

**GET** `/api/menu/categories/{slug}/items/`

Récupère tous les plats disponibles d'une catégorie.

**Permissions:** Accès public

**Réponse 200:**
```json
[
  {
    "id": 5,
    "category": 1,
    "category_name": "Plats principaux",
    "name": "Poulet Yassa",
    "slug": "poulet-yassa",
    "image": "/media/menu_items/poulet-yassa.jpg",
    "is_available": true,
    "preparation_time": 25,
    "min_price": "2500.00",
    "max_price": "4500.00",
    "average_rating": "4.50"
  }
]
```

---

### 2. Plats du menu

**Base URL:** `/api/menu/items/`

#### 2.1 Lister les plats

**GET** `/api/menu/items/`

Récupère la liste des plats avec filtres optionnels.

**Permissions:** Accès public

**Query Parameters:**
- `category` (string, optionnel) : Filtrer par slug de catégorie
- `is_available` (boolean, optionnel) : Filtrer par disponibilité (`true`/`false`)
- `search` (string, optionnel) : Rechercher dans nom, description ou ingrédients

**Exemples:**
- `/api/menu/items/?category=plats-principaux`
- `/api/menu/items/?is_available=true`
- `/api/menu/items/?search=poulet`
- `/api/menu/items/?category=boissons&is_available=true`

**Réponse 200:**
```json
[
  {
    "id": 5,
    "category": 1,
    "category_name": "Plats principaux",
    "name": "Poulet Yassa",
    "slug": "poulet-yassa",
    "image": "/media/menu_items/poulet-yassa.jpg",
    "is_available": true,
    "preparation_time": 25,
    "min_price": "2500.00",
    "max_price": "4500.00",
    "average_rating": "4.50"
  },
  {
    "id": 6,
    "category": 1,
    "category_name": "Plats principaux",
    "name": "Riz Sauce Arachide",
    "slug": "riz-sauce-arachide",
    "image": "/media/menu_items/riz-arachide.jpg",
    "is_available": true,
    "preparation_time": 30,
    "min_price": "2000.00",
    "max_price": "3500.00",
    "average_rating": "4.75"
  }
]
```

---

#### 2.2 Créer un plat

**POST** `/api/menu/items/`

Crée un nouveau plat avec ses formats optionnels.

**Permissions:** Authentification requise

**Body:**
```json
{
  "category": 1,
  "name": "Poulet Braisé",
  "slug": "poulet-braise",
  "description": "Poulet braisé à la perfection avec nos épices maison",
  "image": "<fichier image>",
  "is_available": true,
  "preparation_time": 20,
  "ingredients": "Poulet, oignons, tomates, épices, huile",
  "sizes": [
    {
      "size": "small",
      "price": "2000.00",
      "is_available": true,
      "portion_description": "1/4 de poulet"
    },
    {
      "size": "medium",
      "price": "3500.00",
      "is_available": true,
      "portion_description": "1/2 poulet"
    },
    {
      "size": "large",
      "price": "6000.00",
      "is_available": true,
      "portion_description": "Poulet entier"
    }
  ]
}
```

**Réponse 201:**
```json
{
  "id": 10,
  "category": 1,
  "category_name": "Plats principaux",
  "name": "Poulet Braisé",
  "slug": "poulet-braise",
  "description": "Poulet braisé à la perfection avec nos épices maison",
  "image": "/media/menu_items/poulet-braise.jpg",
  "is_available": true,
  "preparation_time": 20,
  "ingredients": "Poulet, oignons, tomates, épices, huile",
  "sizes": [
    {
      "id": 25,
      "size": "small",
      "size_display": "Petit",
      "price": "2000.00",
      "is_available": true,
      "portion_description": "1/4 de poulet",
      "created_at": "2024-03-15T15:30:00Z",
      "updated_at": "2024-03-15T15:30:00Z"
    },
    {
      "id": 26,
      "size": "medium",
      "size_display": "Normal",
      "price": "3500.00",
      "is_available": true,
      "portion_description": "1/2 poulet",
      "created_at": "2024-03-15T15:30:00Z",
      "updated_at": "2024-03-15T15:30:00Z"
    },
    {
      "id": 27,
      "size": "large",
      "size_display": "Grand",
      "price": "6000.00",
      "is_available": true,
      "portion_description": "Poulet entier",
      "created_at": "2024-03-15T15:30:00Z",
      "updated_at": "2024-03-15T15:30:00Z"
    }
  ],
  "total_orders": 0,
  "average_rating": "0.00",
  "total_ratings": 0,
  "created_at": "2024-03-15T15:30:00Z",
  "updated_at": "2024-03-15T15:30:00Z"
}
```

---

#### 2.3 Détails d'un plat

**GET** `/api/menu/items/{slug}/`

Récupère les détails complets d'un plat, incluant tous ses formats.

**Permissions:** Accès public

**Réponse 200:**
```json
{
  "id": 5,
  "category": 1,
  "category_name": "Plats principaux",
  "name": "Poulet Yassa",
  "slug": "poulet-yassa",
  "description": "Poulet mariné aux oignons et citron, un classique sénégalais",
  "image": "/media/menu_items/poulet-yassa.jpg",
  "is_available": true,
  "preparation_time": 25,
  "ingredients": "Poulet, oignons, citron, moutarde, huile, riz",
  "sizes": [
    {
      "id": 15,
      "size": "small",
      "size_display": "Petit",
      "price": "2500.00",
      "is_available": true,
      "portion_description": "Portion individuelle",
      "created_at": "2024-03-10T10:00:00Z",
      "updated_at": "2024-03-15T12:00:00Z"
    },
    {
      "id": 16,
      "size": "medium",
      "size_display": "Normal",
      "price": "3500.00",
      "is_available": true,
      "portion_description": "Portion généreuse",
      "created_at": "2024-03-10T10:00:00Z",
      "updated_at": "2024-03-15T12:00:00Z"
    },
    {
      "id": 17,
      "size": "large",
      "size_display": "Grand",
      "price": "4500.00",
      "is_available": true,
      "portion_description": "Pour 2 personnes",
      "created_at": "2024-03-10T10:00:00Z",
      "updated_at": "2024-03-15T12:00:00Z"
    }
  ],
  "total_orders": 145,
  "average_rating": "4.50",
  "total_ratings": 32,
  "created_at": "2024-03-10T10:00:00Z",
  "updated_at": "2024-03-15T12:00:00Z"
}
```

---

#### 2.4 Modifier un plat

**PUT/PATCH** `/api/menu/items/{slug}/`

Modifie un plat existant.

**Permissions:** Authentification requise

**Body (PATCH):**
```json
{
  "is_available": false,
  "preparation_time": 30
}
```

**Réponse 200:** Objet plat mis à jour

---

#### 2.5 Supprimer un plat

**DELETE** `/api/menu/items/{slug}/`

Supprime un plat (et tous ses formats en cascade).

**Permissions:** Authentification requise

**Réponse 204:** No Content

---

#### 2.6 Plats populaires

**GET** `/api/menu/items/popular/`

Récupère les 10 plats les plus commandés disponibles.

**Permissions:** Accès public

**Réponse 200:**
```json
[
  {
    "id": 6,
    "category": 1,
    "category_name": "Plats principaux",
    "name": "Riz Sauce Arachide",
    "slug": "riz-sauce-arachide",
    "image": "/media/menu_items/riz-arachide.jpg",
    "is_available": true,
    "preparation_time": 30,
    "min_price": "2000.00",
    "max_price": "3500.00",
    "average_rating": "4.75"
  }
]
```

---

#### 2.7 Plats les mieux notés

**GET** `/api/menu/items/top_rated/`

Récupère les 10 plats disponibles les mieux notés (minimum 5 notes).

**Permissions:** Accès public

**Réponse 200:**
```json
[
  {
    "id": 8,
    "category": 1,
    "category_name": "Plats principaux",
    "name": "Thiéboudienne",
    "slug": "thieboudienne",
    "image": "/media/menu_items/thieboudienne.jpg",
    "is_available": true,
    "preparation_time": 40,
    "min_price": "2500.00",
    "max_price": "4000.00",
    "average_rating": "4.85"
  }
]
```

---

#### 2.8 Notes et avis d'un plat

**GET** `/api/menu/items/{slug}/ratings/`

Récupère toutes les notes et avis d'un plat spécifique.

**Permissions:** Accès public

**Réponse 200:**
```json
{
  "average_rating": 4.5,
  "total_ratings": 32,
  "ratings": [
    {
      "id": 15,
      "order": 123,
      "customer_name": "Marie Kouassi",
      "rating": 5,
      "comment": "Excellent! Le meilleur poulet yassa que j'ai mangé",
      "created_at": "2024-03-15T14:20:00Z"
    },
    {
      "id": 14,
      "order": 118,
      "customer_name": "Jean Mensah",
      "rating": 4,
      "comment": "Très bon, mais un peu épicé pour moi",
      "created_at": "2024-03-14T19:30:00Z"
    }
  ]
}
```

---

#### 2.9 Basculer la disponibilité d'un plat

**POST** `/api/menu/items/{slug}/toggle_availability/`

Active/désactive la disponibilité d'un plat.

**Permissions:** Authentification requise

**Body:** Vide

**Réponse 200:**
```json
{
  "is_available": false
}
```

---

### 3. Formats de plats

**Base URL:** `/api/menu/sizes/`

#### 3.1 Lister les formats

**GET** `/api/menu/sizes/`

Récupère la liste des formats avec filtre optionnel.

**Permissions:** Authentification requise

**Query Parameters:**
- `menu_item` (integer, optionnel) : Filtrer par ID de plat

**Exemple:** `/api/menu/sizes/?menu_item=5`

**Réponse 200:**
```json
[
  {
    "id": 15,
    "size": "small",
    "size_display": "Petit",
    "price": "2500.00",
    "is_available": true,
    "portion_description": "Portion individuelle",
    "created_at": "2024-03-10T10:00:00Z",
    "updated_at": "2024-03-15T12:00:00Z"
  },
  {
    "id": 16,
    "size": "medium",
    "size_display": "Normal",
    "price": "3500.00",
    "is_available": true,
    "portion_description": "Portion généreuse",
    "created_at": "2024-03-10T10:00:00Z",
    "updated_at": "2024-03-15T12:00:00Z"
  }
]
```

---

#### 3.2 Créer un format

**POST** `/api/menu/sizes/`

Crée un nouveau format pour un plat.

**Permissions:** Authentification requise

**Body:**
```json
{
  "menu_item": 5,
  "size": "large",
  "price": "4500.00",
  "is_available": true,
  "portion_description": "Pour 2 personnes"
}
```

**Contrainte:** Un plat ne peut pas avoir deux fois le même format (contrainte unique sur `menu_item` + `size`)

**Réponse 201:**
```json
{
  "id": 17,
  "size": "large",
  "size_display": "Grand",
  "price": "4500.00",
  "is_available": true,
  "portion_description": "Pour 2 personnes",
  "created_at": "2024-03-15T15:45:00Z",
  "updated_at": "2024-03-15T15:45:00Z"
}
```

---

#### 3.3 Détails d'un format

**GET** `/api/menu/sizes/{id}/`

Récupère les détails d'un format spécifique.

**Permissions:** Authentification requise

**Réponse 200:** Objet format (format identique à 3.1)

---

#### 3.4 Modifier un format

**PUT/PATCH** `/api/menu/sizes/{id}/`

Modifie un format existant.

**Permissions:** Authentification requise

**Body (PATCH):**
```json
{
  "price": "4800.00",
  "is_available": true
}
```

**Réponse 200:** Objet format mis à jour

---

#### 3.5 Supprimer un format

**DELETE** `/api/menu/sizes/{id}/`

Supprime un format.

**Permissions:** Authentification requise

**Réponse 204:** No Content

---

#### 3.6 Basculer la disponibilité d'un format

**POST** `/api/menu/sizes/{id}/toggle_availability/`

Active/désactive la disponibilité d'un format spécifique.

**Permissions:** Authentification requise

**Body:** Vide

**Réponse 200:**
```json
{
  "is_available": false
}
```

---

## Flux de travail typique

### Pour un Client (non authentifié):

1. Consulter les catégories: `GET /api/menu/categories/`
2. Voir les plats d'une catégorie: `GET /api/menu/categories/{slug}/items/`
3. Consulter les détails d'un plat: `GET /api/menu/items/{slug}/`
4. Voir les plats populaires: `GET /api/menu/items/popular/`
5. Rechercher un plat: `GET /api/menu/items/?search=poulet`
6. Consulter les avis: `GET /api/menu/items/{slug}/ratings/`

### Pour un Manager:

1. Créer une catégorie: `POST /api/menu/categories/`
2. Créer un plat avec formats: `POST /api/menu/items/`
3. Modifier un plat: `PATCH /api/menu/items/{slug}/`
4. Gérer la disponibilité: `POST /api/menu/items/{slug}/toggle_availability/`
5. Ajouter un format: `POST /api/menu/sizes/`
6. Modifier un format: `PATCH /api/menu/sizes/{id}/`

---

## Formats de tailles disponibles

| Valeur | Libellé | Description typique |
|--------|---------|---------------------|
| `small` | Petit | Portion individuelle |
| `medium` | Normal | Portion standard/généreuse |
| `large` | Grand | Portion familiale/pour 2+ personnes |

---

## Recherche et filtres

### Recherche textuelle
La recherche (`?search=`) interroge les champs:
- `name` (nom du plat)
- `description` (description)
- `ingredients` (liste des ingrédients)

### Exemples de requêtes combinées
```
/api/menu/items/?category=plats-principaux&is_available=true&search=poulet
/api/menu/items/?is_available=true&search=riz
/api/menu/categories/boissons/items/
```

---

## Statistiques et métriques

Chaque plat maintient automatiquement:
- `total_orders`: Nombre total de commandes
- `average_rating`: Note moyenne (0-5)
- `total_ratings`: Nombre total d'évaluations

Ces statistiques sont mises à jour automatiquement via les modules `orders` et `ratings`.

---

## Codes d'erreur communs

- `400 Bad Request`: Données invalides (ex: format dupliqué)
- `401 Unauthorized`: Non authentifié (pour endpoints protégés)
- `403 Forbidden`: Permissions insuffisantes
- `404 Not Found`: Ressource introuvable