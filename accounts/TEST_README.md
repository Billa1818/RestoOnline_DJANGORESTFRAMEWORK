# Tests des Endpoints - Application Accounts

Ce document décrit comment utiliser le fichier de tests pour tester tous les endpoints de l'application `accounts`.

## 📋 Vue d'ensemble

Le fichier `test_accounts_endpoints.py` contient des tests complets pour tous les endpoints de l'application accounts, utilisant la bibliothèque `requests` pour effectuer des requêtes HTTP réelles.

## 🎯 Endpoints testés

### 1. Authentification
- ✅ `POST /api/accounts/users/login/` - Connexion utilisateur
- ✅ `POST /api/accounts/users/login/` - Connexion avec identifiants invalides
- ✅ `GET /api/accounts/users/me/` - Profil utilisateur connecté
- ✅ `POST /api/accounts/users/change_password/` - Changer mot de passe
- ✅ `POST /api/accounts/users/password_reset_request/` - Demande réinitialisation

### 2. Gestion des utilisateurs (CRUD)
- ✅ `GET /api/accounts/users/` - Liste des utilisateurs
- ✅ `GET /api/accounts/users/?user_type=delivery` - Filtrage par type
- ✅ `POST /api/accounts/users/` - Créer un utilisateur
- ✅ `GET /api/accounts/users/{id}/` - Détails d'un utilisateur
- ✅ `PATCH /api/accounts/users/{id}/` - Modifier un utilisateur
- ✅ `DELETE /api/accounts/users/{id}/` - Supprimer un utilisateur

### 3. Gestion des livreurs
- ✅ `POST /api/accounts/users/{id}/toggle_availability/` - Basculer disponibilité
- ✅ `GET /api/accounts/delivery-persons/` - Liste des livreurs
- ✅ `GET /api/accounts/delivery-persons/available/` - Livreurs disponibles
- ✅ `GET /api/accounts/delivery-persons/{id}/` - Détails d'un livreur
- ✅ `GET /api/accounts/delivery-persons/{id}/statistics/` - Statistiques livreur

### 4. Appareils clients (Device-Based Auth)
- ✅ `POST /api/accounts/devices/register/` - Enregistrer un appareil
- ✅ `GET /api/accounts/devices/` - Liste des appareils
- ✅ `GET /api/accounts/devices/{device_id}/` - Détails d'un appareil
- ✅ `PATCH /api/accounts/devices/{device_id}/update-info/` - Mettre à jour infos client
- ✅ `PATCH /api/accounts/devices/{device_id}/` - Modifier un appareil
- ✅ `GET /api/accounts/devices/{device_id}/orders/` - Commandes d'un appareil
- ✅ `DELETE /api/accounts/devices/{device_id}/` - Supprimer un appareil

**Total: 25 tests**

## 🔧 Prérequis

### Installation des dépendances

```bash
pip install requests
```

### Configuration du serveur

1. **Démarrer le serveur Django:**
   ```bash
   cd RestoOnline
   python manage.py runserver
   ```

2. **Créer un utilisateur admin pour les tests:**
   ```bash
   python manage.py createsuperuser
   ```
   
   Utilisez ces identifiants par défaut (ou modifiez-les dans le fichier de test):
   - Username: `admin`
   - Password: `admin123`

3. **Appliquer les migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## 🚀 Utilisation

### Méthode 1: Exécution directe

```bash
cd RestoOnline/accounts
python test_accounts_endpoints.py
```

### Méthode 2: Avec URL personnalisée

```bash
python test_accounts_endpoints.py http://localhost:8000/api/accounts
```

### Méthode 3: Depuis le répertoire RestoOnline

```bash
cd RestoOnline
python accounts/test_accounts_endpoints.py
```

## 📊 Résultats des tests

Les tests affichent des résultats colorés pour une meilleure lisibilité:

- ✅ **PASS** en vert - Test réussi
- ❌ **FAIL** en rouge - Test échoué
- ℹ️ Messages d'information en jaune

### Exemple de sortie:

```
============================================================
DÉMARRAGE DES TESTS - ACCOUNTS APP
============================================================

Section 1: AUTHENTIFICATION

✓ PASS - Login utilisateur
  → Token obtenu, user_type: admin

✓ PASS - Login avec identifiants invalides
  → Status: 401 (attendu: 401)

✓ PASS - Récupérer profil utilisateur connecté
  → Username: admin, Type: admin

[...]

============================================================
RÉSUMÉ DES TESTS
============================================================
Total: 25 tests
Réussis: 25
Échoués: 0

🎉 Tous les tests ont réussi !
============================================================
```

## 🔐 Configuration

### Modifier les identifiants de connexion

Éditez le fichier `test_accounts_endpoints.py`, ligne ~90:

```python
def test_login(self):
    url = f"{self.base_url}/users/login/"
    data = {
        "username": "admin",  # ← Modifiez ici
        "password": "admin123"  # ← Modifiez ici
    }
```

### Modifier l'URL de base

Éditez la ligne ~16 du fichier:

```python
BASE_URL = "http://localhost:8000"  # ← Modifiez ici
```

## 📝 Structure du code

### Classe principale: `AccountsEndpointTester`

```python
class AccountsEndpointTester:
    - get_headers()         # Génère les headers HTTP
    - print_result()        # Affiche les résultats
    - print_summary()       # Affiche le résumé
    - test_*()              # Méthodes de test individuelles
    - run_all_tests()       # Exécute tous les tests
```

### Fonctionnalités

1. **Authentification JWT**: Gère automatiquement les tokens d'accès
2. **Tests séquentiels**: Les tests s'exécutent dans un ordre logique
3. **Gestion d'état**: Conserve les IDs créés pour les tests suivants
4. **Nettoyage**: Supprime les données de test à la fin
5. **Rapports détaillés**: Affiche des informations sur chaque test

## 🧪 Personnalisation

### Ajouter un nouveau test

```python
def test_mon_nouveau_test(self):
    """Test: Description du test"""
    url = f"{self.base_url}/mon-endpoint/"
    
    try:
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            self.print_result(
                "Nom du test",
                True,
                f"Info: {result.get('data')}"
            )
            return True
        else:
            self.print_result(
                "Nom du test",
                False,
                f"Status {response.status_code}: {response.text}"
            )
            return False
    except Exception as e:
        self.print_result("Nom du test", False, str(e))
        return False
```

Puis ajoutez-le dans `run_all_tests()`:

```python
def run_all_tests(self):
    # ...
    self.test_mon_nouveau_test()
    # ...
```

## ⚠️ Notes importantes

1. **Serveur doit être actif**: Assurez-vous que Django tourne sur le port 8000
2. **Base de données**: Les tests créent et suppriment des données
3. **Authentification**: Un utilisateur admin doit exister
4. **Ordre des tests**: Les tests dépendent les uns des autres
5. **Données de test**: Utilisent des UUID pour éviter les conflits

## 🐛 Dépannage

### Erreur de connexion

```
Connection refused
```
**Solution**: Démarrez le serveur Django

### Erreur d'authentification

```
Status 401: Unauthorized
```
**Solution**: Vérifiez les identifiants dans `test_login()`

### Module non trouvé

```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: `pip install requests`

### Tests échouent

1. Vérifiez que le serveur est démarré
2. Vérifiez les migrations: `python manage.py migrate`
3. Vérifiez l'utilisateur admin existe
4. Consultez les logs du serveur Django

## 📚 Documentation des endpoints

Pour plus de détails sur les endpoints, consultez:
- `RestoOnline/accounts/urls.py` - Routes définies
- `RestoOnline/accounts/views.py` - Logique des endpoints
- `RestoOnline/accounts/readme.md` - Documentation de l'app

## 🔄 Intégration continue

Pour intégrer ces tests dans un pipeline CI/CD:

```bash
# Script de test automatisé
#!/bin/bash

# Démarrer le serveur en arrière-plan
python manage.py runserver &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 5

# Exécuter les tests
python accounts/test_accounts_endpoints.py

# Arrêter le serveur
kill $SERVER_PID
```

## 📞 Support

Pour toute question ou problème:
1. Vérifiez d'abord la documentation Django
2. Consultez les logs du serveur
3. Vérifiez la configuration de l'API

---

**Fichier créé le**: 27/11/2025  
**Version**: 1.0  
**Auteur**: Test Suite pour RostoOnline Backend
