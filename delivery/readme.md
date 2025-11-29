# Documentation API - Module Delivery

## Endpoints

### 1. Affectations de livraison

**Base URL:** `/api/delivery/assignments/`

#### 1.1 Lister les affectations

**GET** `/api/delivery/assignments/`

Récupère la liste des affectations de livraison avec filtres optionnels.

**Permissions:** Authentification requise

**Query Parameters:**
- `status` (string, optionnel) : Filtrer par statut (`assigned`, `accepted`, `refused`, `picked_up`, `delivered`)
- `delivery_person_id` (integer, optionnel) : Filtrer par ID du livreur

**Comportement selon le type d'utilisateur:**
- Les livreurs ne voient que leurs propres affectations
- Les managers voient toutes les affectations

**Réponse 200:**
```json
[
  {
    "id": 1,
    "order_number": "CMD-2024-001",
    "delivery_person_name": "Jean Dupont",
    "customer_name": "Marie Martin",
    "status": "accepted",
    "status_display": "Acceptée",
    "assigned_at": "2024-03-15T10:30:00Z",
    "delivered_at": null
  }
]
```

---

#### 1.2 Créer une affectation

**POST** `/api/delivery/assignments/`

Assigne une commande à un livreur.

**Permissions:** Authentification requise (Manager)

**Body:**
```json
{
  "order": 1,
  "delivery_person": 5,
  "assigned_by": 2,
  "notes": "Livraison urgente"
}
```

**Validations:**
- La commande doit exister et avoir le statut `ready`
- La commande ne doit pas déjà être assignée
- L'utilisateur assigné doit être un livreur (`user_type: 'delivery'`)

**Réponse 201:**
```json
{
  "id": 1,
  "order": 1,
  "order_details": {
    "id": 1,
    "order_number": "CMD-2024-001",
    "customer_name": "Marie Martin",
    "total_price": "25.50",
    "status": "assigned"
  },
  "delivery_person": 5,
  "delivery_person_details": {
    "id": 5,
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+22997123456",
    "is_available": true,
    "total_deliveries": 45
  },
  "assigned_by": 2,
  "assigned_by_name": "Admin Manager",
  "status": "assigned",
  "status_display": "Assignée",
  "assigned_at": "2024-03-15T10:30:00Z",
  "accepted_at": null,
  "refused_at": null,
  "picked_up_at": null,
  "delivered_at": null,
  "refusal_reason": "",
  "notes": "Livraison urgente",
  "latest_location": null
}
```

**Erreurs possibles:**
- `404` : Commande non trouvée
- `400` : Commande déjà assignée ou statut invalide

---

#### 1.3 Détails d'une affectation

**GET** `/api/delivery/assignments/{id}/`

Récupère les détails complets d'une affectation.

**Permissions:** Authentification requise

**Réponse 200:**
```json
{
  "id": 1,
  "order": 1,
  "order_details": {
    "id": 1,
    "order_number": "CMD-2024-001",
    "customer_name": "Marie Martin",
    "customer_phone": "+22997654321",
    "delivery_address": "Cotonou, Akpakpa",
    "total_price": "25.50",
    "status": "in_delivery"
  },
  "delivery_person": 5,
  "delivery_person_details": {
    "id": 5,
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+22997123456",
    "vehicle_type": "moto",
    "is_available": false,
    "total_deliveries": 45
  },
  "assigned_by": 2,
  "assigned_by_name": "Admin Manager",
  "status": "picked_up",
  "status_display": "Récupérée",
  "assigned_at": "2024-03-15T10:30:00Z",
  "accepted_at": "2024-03-15T10:35:00Z",
  "refused_at": null,
  "picked_up_at": "2024-03-15T10:45:00Z",
  "delivered_at": null,
  "refusal_reason": "",
  "notes": "Livraison urgente",
  "latest_location": {
    "id": 15,
    "latitude": "6.3654200",
    "longitude": "2.4183800",
    "accuracy": 10.5,
    "timestamp": "2024-03-15T11:00:00Z"
  }
}
```

---

#### 1.4 Mes livraisons (Livreur)

**GET** `/api/delivery/assignments/my_deliveries/`

Récupère toutes les affectations du livreur connecté.

**Permissions:** Authentification requise (Livreur uniquement)

**Réponse 200:** Liste d'affectations (format identique à 1.1)

**Erreur 403:** Si l'utilisateur n'est pas un livreur

---

#### 1.5 Affectations en attente

**GET** `/api/delivery/assignments/pending/`

Récupère les affectations avec le statut `assigned` (en attente d'acceptation).

**Permissions:** Authentification requise

**Réponse 200:** Liste d'affectations en attente

---

#### 1.6 Livraisons actives

**GET** `/api/delivery/assignments/active/`

Récupère les livraisons en cours (statuts `accepted` ou `picked_up`).

**Permissions:** Authentification requise

**Réponse 200:** Liste des livraisons actives

---

#### 1.7 Accepter une affectation

**POST** `/api/delivery/assignments/{id}/accept/`

Le livreur accepte une affectation qui lui a été assignée.

**Permissions:** Authentification requise (Livreur)

**Body:** Vide

**Validations:**
- Le livreur connecté doit être le livreur assigné
- Le statut doit être `assigned`

**Réponse 200:**
```json
{
  "id": 1,
  "status": "accepted",
  "status_display": "Acceptée",
  "accepted_at": "2024-03-15T10:35:00Z",
  ...
}
```

**Erreurs possibles:**
- `403` : Livreur non autorisé
- `400` : Statut invalide pour l'acceptation

---

#### 1.8 Refuser une affectation

**POST** `/api/delivery/assignments/{id}/refuse/`

Le livreur refuse une affectation.

**Permissions:** Authentification requise (Livreur)

**Body:**
```json
{
  "reason": "Véhicule en panne"
}
```

**Validations:**
- Le livreur connecté doit être le livreur assigné
- Le statut doit être `assigned`

**Comportement:**
- La commande repasse au statut `ready`
- Le champ `delivery_person` de la commande est réinitialisé

**Réponse 200:**
```json
{
  "id": 1,
  "status": "refused",
  "status_display": "Refusée",
  "refused_at": "2024-03-15T10:33:00Z",
  "refusal_reason": "Véhicule en panne",
  ...
}
```

---

#### 1.9 Confirmer la récupération

**POST** `/api/delivery/assignments/{id}/pickup/`

Le livreur confirme avoir récupéré la commande.

**Permissions:** Authentification requise (Livreur)

**Body:** Vide

**Validations:**
- Le livreur connecté doit être le livreur assigné
- Le statut doit être `accepted`

**Comportement:**
- Le statut de l'affectation passe à `picked_up`
- Le statut de la commande passe à `in_delivery`

**Réponse 200:**
```json
{
  "id": 1,
  "status": "picked_up",
  "status_display": "Récupérée",
  "picked_up_at": "2024-03-15T10:45:00Z",
  ...
}
```

---

#### 1.10 Marquer comme livrée

**POST** `/api/delivery/assignments/{id}/complete/`

Le livreur confirme avoir livré la commande.

**Permissions:** Authentification requise (Livreur)

**Body:** Vide

**Validations:**
- Le livreur connecté doit être le livreur assigné
- Le statut doit être `picked_up`

**Comportement:**
- Le statut de l'affectation passe à `delivered`
- Le statut de la commande passe à `delivered`
- Le compteur `total_deliveries` du livreur est incrémenté

**Réponse 200:**
```json
{
  "id": 1,
  "status": "delivered",
  "status_display": "Livrée",
  "delivered_at": "2024-03-15T11:15:00Z",
  ...
}
```

---

#### 1.11 Mettre à jour la position

**POST** `/api/delivery/assignments/{id}/update_location/`

Le livreur envoie sa position GPS actuelle.

**Permissions:** Authentification requise (Livreur)

**Body:**
```json
{
  "latitude": 6.3654200,
  "longitude": 2.4183800,
  "accuracy": 10.5
}
```

**Validations:**
- Le livreur connecté doit être le livreur assigné
- `latitude` et `longitude` sont obligatoires

**Réponse 201:**
```json
{
  "id": 15,
  "assignment": 1,
  "latitude": "6.3654200",
  "longitude": "2.4183800",
  "accuracy": 10.5,
  "timestamp": "2024-03-15T11:00:00Z"
}
```

---

#### 1.12 Historique de suivi

**GET** `/api/delivery/assignments/{id}/tracking/`

Récupère les 20 dernières positions enregistrées pour une affectation.

**Permissions:** Authentification requise

**Réponse 200:**
```json
[
  {
    "id": 15,
    "assignment": 1,
    "latitude": "6.3654200",
    "longitude": "2.4183800",
    "accuracy": 10.5,
    "timestamp": "2024-03-15T11:00:00Z"
  },
  {
    "id": 14,
    "assignment": 1,
    "latitude": "6.3650000",
    "longitude": "2.4180000",
    "accuracy": 12.0,
    "timestamp": "2024-03-15T10:58:00Z"
  }
]
```

---

### 2. Positions de livraison

**Base URL:** `/api/delivery/locations/`

#### 2.1 Lister les positions

**GET** `/api/delivery/locations/`

Récupère la liste des positions GPS enregistrées.

**Permissions:** Authentification requise

**Query Parameters:**
- `assignment_id` (integer, optionnel) : Filtrer par ID d'affectation

**Réponse 200:**
```json
[
  {
    "id": 15,
    "assignment": 1,
    "latitude": "6.3654200",
    "longitude": "2.4183800",
    "accuracy": 10.5,
    "timestamp": "2024-03-15T11:00:00Z"
  }
]
```

---

#### 2.2 Détails d'une position

**GET** `/api/delivery/locations/{id}/`

Récupère les détails d'une position spécifique.

**Permissions:** Authentification requise

**Réponse 200:** Objet position (format identique à 2.1)

---

## Flux de travail typique

### Pour un Manager:

1. Créer une affectation: `POST /api/delivery/assignments/`
2. Suivre les livraisons actives: `GET /api/delivery/assignments/active/`
3. Consulter l'historique: `GET /api/delivery/assignments/{id}/tracking/`

### Pour un Livreur:

1. Voir ses affectations: `GET /api/delivery/assignments/my_deliveries/`
2. Accepter une livraison: `POST /api/delivery/assignments/{id}/accept/`
3. Confirmer la récupération: `POST /api/delivery/assignments/{id}/pickup/`
4. Envoyer sa position régulièrement: `POST /api/delivery/assignments/{id}/update_location/`
5. Marquer comme livrée: `POST /api/delivery/assignments/{id}/complete/`

---

## Statuts des affectations

| Statut | Description | Actions possibles |
|--------|-------------|-------------------|
| `assigned` | Assignée au livreur | Accepter ou refuser |
| `accepted` | Acceptée par le livreur | Confirmer récupération |
| `refused` | Refusée par le livreur | Aucune (terminal) |
| `picked_up` | Commande récupérée | Marquer comme livrée |
| `delivered` | Livraison terminée | Aucune (terminal) |

---

## Codes d'erreur communs

- `400 Bad Request` : Données invalides ou action non autorisée
- `401 Unauthorized` : Non authentifié
- `403 Forbidden` : Permissions insuffisantes
- `404 Not Found` : Ressource introuvable