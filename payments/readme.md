# Documentation des Endpoints - Application Payments

## Vue d'ensemble
Cette application gère les paiements via PayDunya (Orange Money, MTN Mobile Money, Moov Money, etc.) pour les commandes.

---

## Endpoints Payments

### 1. Lister les paiements
```
GET /api/payments/
```

**Permissions:** Authentification requise

**Paramètres de requête (optionnels):**
- `order_id` - Filtrer par ID de commande
- `status` - Filtrer par statut (`pending`, `processing`, `completed`, `failed`, `cancelled`, `refunded`)
- `payment_method` - Filtrer par méthode (`orange_money`, `mtn_money`, `moov_money`, `card`, `cash`)

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "order": 5,
    "order_number": "CMD-2024-001",
    "paydunya_token": "abc123xyz",
    "paydunya_invoice_url": "https://app.paydunya.com/invoice/abc123xyz",
    "paydunya_response_code": "00",
    "paydunya_response_text": "Success",
    "amount": "15000.00",
    "payment_method": "orange_money",
    "payment_method_display": "Orange Money",
    "status": "completed",
    "status_display": "Complété",
    "transaction_id": "TXN123456789",
    "paydunya_response": {},
    "notes": "",
    "created_at": "2024-11-27T10:00:00Z",
    "completed_at": "2024-11-27T10:05:00Z",
    "updated_at": "2024-11-27T10:05:00Z"
  }
]
```

---

### 2. Créer un paiement
```
POST /api/payments/
```

**Permissions:** Accès public (AllowAny)

**Corps de la requête:**
```json
{
  "order": 5,
  "amount": "15000.00",
  "payment_method": "orange_money"
}
```

**Champs:**
- `order` (integer, requis) - ID de la commande
- `amount` (decimal, requis) - Montant du paiement
- `payment_method` (string, requis) - Méthode de paiement

**Réponse succès (201 Created):**
```json
{
  "id": 1,
  "order": 5,
  "order_number": "CMD-2024-001",
  "paydunya_token": "abc123xyz",
  "paydunya_invoice_url": "https://app.paydunya.com/invoice/abc123xyz",
  "paydunya_response_code": "00",
  "paydunya_response_text": "Success",
  "amount": "15000.00",
  "payment_method": "orange_money",
  "payment_method_display": "Orange Money",
  "status": "processing",
  "status_display": "En cours",
  "transaction_id": "",
  "paydunya_response": {
    "success": true,
    "token": "abc123xyz",
    "invoice_url": "https://app.paydunya.com/invoice/abc123xyz"
  },
  "notes": "",
  "created_at": "2024-11-27T10:00:00Z",
  "completed_at": null,
  "updated_at": "2024-11-27T10:00:00Z"
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
  "error": "Un paiement existe déjà pour cette commande"
}
```

---

### 3. Détails d'un paiement
```
GET /api/payments/{id}/
```

**Permissions:** Authentification requise

**Réponse (200 OK):**
```json
{
  "id": 1,
  "order": 5,
  "order_number": "CMD-2024-001",
  "paydunya_token": "abc123xyz",
  "paydunya_invoice_url": "https://app.paydunya.com/invoice/abc123xyz",
  "amount": "15000.00",
  "payment_method": "orange_money",
  "status": "completed",
  "transaction_id": "TXN123456789",
  "created_at": "2024-11-27T10:00:00Z",
  "completed_at": "2024-11-27T10:05:00Z"
}
```

---

### 4. Vérifier le statut d'un paiement
```
GET /api/payments/{id}/check_status/
```

**Permissions:** Accès public (AllowAny)

**Description:** Vérifie le statut du paiement auprès de PayDunya et met à jour automatiquement le paiement et la commande si le paiement est complété.

**Réponse (200 OK):**
```json
{
  "id": 1,
  "order": 5,
  "order_number": "CMD-2024-001",
  "status": "completed",
  "transaction_id": "TXN123456789",
  "completed_at": "2024-11-27T10:05:00Z"
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "Token PayDunya manquant"
}
```

---

### 5. Statistiques des paiements
```
GET /api/payments/statistics/
```

**Permissions:** Authentification requise

**Description:** Retourne des statistiques globales et par méthode de paiement.

**Réponse (200 OK):**
```json
{
  "total_payments": 150,
  "completed_count": 120,
  "pending_count": 20,
  "failed_count": 10,
  "total_amount": 1500000.00,
  "by_method": {
    "orange_money": {
      "count": 70,
      "total_amount": 850000.00
    },
    "mtn_money": {
      "count": 35,
      "total_amount": 450000.00
    },
    "moov_money": {
      "count": 10,
      "total_amount": 150000.00
    },
    "card": {
      "count": 5,
      "total_amount": 50000.00
    },
    "cash": {
      "count": 0,
      "total_amount": 0.00
    }
  }
}
```

---

## Endpoint Webhook PayDunya

### 6. Webhook PayDunya
```
POST /api/paydunya/webhook/
```

**Permissions:** Accès public (AllowAny)

**Description:** Endpoint appelé automatiquement par PayDunya pour notifier du statut d'un paiement.

**Corps de la requête (exemple PayDunya):**
```json
{
  "token": "abc123xyz",
  "status": "completed",
  "transaction_id": "TXN123456789",
  "amount": "15000.00",
  "custom_data": {
    "order_id": "5",
    "order_number": "CMD-2024-001"
  }
}
```

**Réponse succès (200 OK):**
```json
{
  "success": true
}
```

**Réponse erreur (400 Bad Request):**
```json
{
  "error": "Token manquant"
}
```

**Réponse erreur (404 Not Found):**
```json
{
  "error": "Paiement non trouvé"
}
```

**Actions automatiques:**
- Crée un enregistrement `PaymentWebhook`
- Met à jour le statut du paiement
- Si le paiement est complété et la commande est en `pending`, passe la commande en `accepted`

---

## Endpoints Webhooks (Logs)

### 7. Lister les webhooks
```
GET /api/webhooks/
```

**Permissions:** Authentification requise

**Paramètres de requête (optionnels):**
- `processed` - Filtrer par statut de traitement (`true` ou `false`)
- `payment_id` - Filtrer par ID de paiement

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "payment": 5,
    "webhook_data": {
      "token": "abc123xyz",
      "status": "completed",
      "transaction_id": "TXN123456789"
    },
    "status": "completed",
    "processed": true,
    "processing_error": "",
    "received_at": "2024-11-27T10:05:00Z",
    "processed_at": "2024-11-27T10:05:01Z"
  }
]
```

---

### 8. Détails d'un webhook
```
GET /api/webhooks/{id}/
```

**Permissions:** Authentification requise

**Réponse (200 OK):**
```json
{
  "id": 1,
  "payment": 5,
  "webhook_data": {...},
  "status": "completed",
  "processed": true,
  "processing_error": "",
  "received_at": "2024-11-27T10:05:00Z",
  "processed_at": "2024-11-27T10:05:01Z"
}
```

---

### 9. Webhooks non traités
```
GET /api/webhooks/unprocessed/
```

**Permissions:** Authentification requise

**Description:** Retourne uniquement les webhooks qui n'ont pas encore été traités.

**Réponse (200 OK):**
```json
[
  {
    "id": 2,
    "payment": null,
    "webhook_data": {...},
    "status": "pending",
    "processed": false,
    "processing_error": "Paiement non trouvé",
    "received_at": "2024-11-27T10:10:00Z",
    "processed_at": null
  }
]
```

---

## Codes de statut des paiements

| Code | Libellé | Description |
|------|---------|-------------|
| `pending` | En attente | Paiement initialisé, en attente de traitement |
| `processing` | En cours | Paiement en cours de traitement par PayDunya |
| `completed` | Complété | Paiement réussi |
| `failed` | Échoué | Paiement échoué |
| `cancelled` | Annulé | Paiement annulé par l'utilisateur |
| `refunded` | Remboursé | Paiement remboursé |

---

## Méthodes de paiement

| Code | Libellé |
|------|---------|
| `orange_money` | Orange Money |
| `mtn_money` | MTN Mobile Money |
| `moov_money` | Moov Money |
| `card` | Carte bancaire |
| `cash` | Espèces |

---

## Flux de paiement typique

1. **Client crée un paiement** → `POST /api/payments/`
   - Reçoit l'URL de la facture PayDunya
   - Statut: `processing`

2. **Client est redirigé vers PayDunya** → Utilise `paydunya_invoice_url`

3. **Client effectue le paiement sur PayDunya**

4. **PayDunya notifie l'application** → `POST /api/paydunya/webhook/`
   - Statut mis à jour automatiquement en `completed`
   - Commande passée en `accepted`

5. **Vérification optionnelle** → `GET /api/payments/{id}/check_status/`

---

## Notes importantes

- **Sécurité:** Les endpoints de création et de vérification sont publics pour faciliter l'intégration frontend
- **Webhook:** L'URL du webhook doit être configurée dans le dashboard PayDunya
- **Configuration:** Nécessite les clés API PayDunya dans `settings.py`
- **Bibliothèque:** Utilise le package Python `paydunya` (à installer via pip)