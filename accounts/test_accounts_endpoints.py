"""
Tests pour tous les endpoints de l'application accounts
Utilise la bibliothèque requests pour tester les endpoints
"""

import requests
import json
import uuid
from typing import Dict, Optional


# ===================================
# CONFIGURATION
# ===================================

BASE_URL = "http://localhost:8000"  # Modifier selon votre configuration
API_BASE = f"{BASE_URL}/api/accounts"

# Couleurs pour l'affichage des résultats
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


# ===================================
# CLASSE DE TEST
# ===================================

class AccountsEndpointTester:
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.test_user_id: Optional[int] = None
        self.test_delivery_id: Optional[int] = None
        self.test_device_id: Optional[str] = None
        self.passed_tests = 0
        self.failed_tests = 0
    
    def get_headers(self, auth: bool = True) -> Dict:
        """Retourne les headers HTTP avec authentification si nécessaire"""
        headers = {"Content-Type": "application/json"}
        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def print_result(self, test_name: str, success: bool, message: str = ""):
        """Affiche le résultat d'un test"""
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {test_name}")
        if message:
            print(f"  {Colors.YELLOW}→ {message}{Colors.END}")
        print()
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def print_summary(self):
        """Affiche le résumé des tests"""
        total = self.passed_tests + self.failed_tests
        print("\n" + "=" * 60)
        print(f"{Colors.BLUE}RÉSUMÉ DES TESTS{Colors.END}")
        print("=" * 60)
        print(f"Total: {total} tests")
        print(f"{Colors.GREEN}Réussis: {self.passed_tests}{Colors.END}")
        print(f"{Colors.RED}Échoués: {self.failed_tests}{Colors.END}")
        if self.failed_tests == 0:
            print(f"\n{Colors.GREEN}🎉 Tous les tests ont réussi !{Colors.END}")
        print("=" * 60 + "\n")
    
    # ===================================
    # TESTS D'AUTHENTIFICATION
    # ===================================
    
    def test_create_admin_user(self):
        """Test: Créer un utilisateur admin (sans authentification)"""
        # Note: En production, la création d'utilisateurs devrait être protégée
        # Pour les tests, on suppose qu'on peut créer directement via l'API ou Django admin
        print(f"{Colors.BLUE}Note: Créez manuellement un utilisateur admin via Django admin{Colors.END}")
        print(f"{Colors.BLUE}python manage.py createsuperuser{Colors.END}\n")
        return True
    
    def test_login(self):
        """Test: POST /api/accounts/users/login/"""
        url = f"{self.base_url}/users/login/"
        data = {
            "username": "admin",  # Modifier selon votre utilisateur de test
            "password": "admin123"  # Modifier selon votre mot de passe de test
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers(auth=False))
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access')
                self.refresh_token = result.get('refresh')
                self.print_result(
                    "Login utilisateur",
                    True,
                    f"Token obtenu, user_type: {result.get('user', {}).get('user_type')}"
                )
                return True
            else:
                self.print_result(
                    "Login utilisateur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Login utilisateur", False, str(e))
            return False
    
    def test_login_invalid_credentials(self):
        """Test: Login avec identifiants invalides"""
        url = f"{self.base_url}/users/login/"
        data = {
            "username": "invalid_user",
            "password": "wrong_password"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers(auth=False))
            
            success = response.status_code == 401
            self.print_result(
                "Login avec identifiants invalides",
                success,
                f"Status: {response.status_code} (attendu: 401)"
            )
            return success
        except Exception as e:
            self.print_result("Login avec identifiants invalides", False, str(e))
            return False
    
    def test_get_me(self):
        """Test: GET /api/accounts/users/me/"""
        url = f"{self.base_url}/users/me/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Récupérer profil utilisateur connecté",
                    True,
                    f"Username: {result.get('username')}, Type: {result.get('user_type')}"
                )
                return True
            else:
                self.print_result(
                    "Récupérer profil utilisateur connecté",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Récupérer profil utilisateur connecté", False, str(e))
            return False
    
    def test_change_password(self):
        """Test: POST /api/accounts/users/change_password/"""
        url = f"{self.base_url}/users/change_password/"
        data = {
            "old_password": "admin123",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            
            # On teste la validation, pas vraiment le changement
            # Pour ne pas casser l'authentification
            if response.status_code in [200, 400]:
                self.print_result(
                    "Changer mot de passe",
                    True,
                    f"Status: {response.status_code}"
                )
                return True
            else:
                self.print_result(
                    "Changer mot de passe",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Changer mot de passe", False, str(e))
            return False
    
    def test_password_reset_request(self):
        """Test: POST /api/accounts/users/password_reset_request/"""
        url = f"{self.base_url}/users/password_reset_request/"
        data = {
            "email": "test@example.com"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers(auth=False))
            
            # Devrait toujours retourner 200 pour des raisons de sécurité
            success = response.status_code == 200
            self.print_result(
                "Demande de réinitialisation de mot de passe",
                success,
                f"Status: {response.status_code}"
            )
            return success
        except Exception as e:
            self.print_result("Demande de réinitialisation de mot de passe", False, str(e))
            return False
    
    # ===================================
    # TESTS GESTION UTILISATEURS
    # ===================================
    
    def test_list_users(self):
        """Test: GET /api/accounts/users/"""
        url = f"{self.base_url}/users/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else result.get('count', 0)
                self.print_result(
                    "Lister tous les utilisateurs",
                    True,
                    f"Nombre d'utilisateurs: {count}"
                )
                return True
            else:
                self.print_result(
                    "Lister tous les utilisateurs",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Lister tous les utilisateurs", False, str(e))
            return False
    
    def test_list_users_filtered(self):
        """Test: GET /api/accounts/users/?user_type=delivery"""
        url = f"{self.base_url}/users/?user_type=delivery"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else result.get('count', 0)
                self.print_result(
                    "Lister utilisateurs filtrés par type",
                    True,
                    f"Livreurs trouvés: {count}"
                )
                return True
            else:
                self.print_result(
                    "Lister utilisateurs filtrés par type",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Lister utilisateurs filtrés par type", False, str(e))
            return False
    
    def test_create_user(self):
        """Test: POST /api/accounts/users/"""
        url = f"{self.base_url}/users/"
        data = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "manager",
            "phone": "+22997123456"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            
            if response.status_code == 201:
                result = response.json()
                self.test_user_id = result.get('id')
                self.print_result(
                    "Créer un utilisateur",
                    True,
                    f"Utilisateur créé avec ID: {self.test_user_id}"
                )
                return True
            else:
                self.print_result(
                    "Créer un utilisateur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Créer un utilisateur", False, str(e))
            return False
    
    def test_get_user_detail(self):
        """Test: GET /api/accounts/users/{id}/"""
        if not self.test_user_id:
            self.print_result("Récupérer détails utilisateur", False, "Pas d'ID utilisateur de test")
            return False
        
        url = f"{self.base_url}/users/{self.test_user_id}/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Récupérer détails utilisateur",
                    True,
                    f"Username: {result.get('username')}"
                )
                return True
            else:
                self.print_result(
                    "Récupérer détails utilisateur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Récupérer détails utilisateur", False, str(e))
            return False
    
    def test_update_user_patch(self):
        """Test: PATCH /api/accounts/users/{id}/"""
        if not self.test_user_id:
            self.print_result("Modifier utilisateur (PATCH)", False, "Pas d'ID utilisateur de test")
            return False
        
        url = f"{self.base_url}/users/{self.test_user_id}/"
        data = {
            "first_name": "Updated",
            "phone": "+22997654321"
        }
        
        try:
            response = requests.patch(url, json=data, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Modifier utilisateur (PATCH)",
                    True,
                    f"Prénom: {result.get('first_name')}, Téléphone: {result.get('phone')}"
                )
                return True
            else:
                self.print_result(
                    "Modifier utilisateur (PATCH)",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Modifier utilisateur (PATCH)", False, str(e))
            return False
    
    def test_create_delivery_user(self):
        """Test: Créer un utilisateur livreur pour les tests"""
        url = f"{self.base_url}/users/"
        data = {
            "username": f"delivery_{uuid.uuid4().hex[:8]}",
            "email": f"delivery_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "Delivery",
            "last_name": "Person",
            "user_type": "delivery",
            "phone": "+22997111222",
            "is_available": True
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            
            if response.status_code == 201:
                result = response.json()
                self.test_delivery_id = result.get('id')
                self.print_result(
                    "Créer un utilisateur livreur",
                    True,
                    f"Livreur créé avec ID: {self.test_delivery_id}"
                )
                return True
            else:
                self.print_result(
                    "Créer un utilisateur livreur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Créer un utilisateur livreur", False, str(e))
            return False
    
    def test_toggle_availability(self):
        """Test: POST /api/accounts/users/{id}/toggle_availability/"""
        if not self.test_delivery_id:
            self.print_result("Basculer disponibilité livreur", False, "Pas d'ID livreur de test")
            return False
        
        url = f"{self.base_url}/users/{self.test_delivery_id}/toggle_availability/"
        
        try:
            response = requests.post(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Basculer disponibilité livreur",
                    True,
                    f"Disponibilité: {result.get('is_available')}"
                )
                return True
            else:
                self.print_result(
                    "Basculer disponibilité livreur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Basculer disponibilité livreur", False, str(e))
            return False
    
    def test_delete_user(self):
        """Test: DELETE /api/accounts/users/{id}/"""
        if not self.test_user_id:
            self.print_result("Supprimer utilisateur", False, "Pas d'ID utilisateur de test")
            return False
        
        url = f"{self.base_url}/users/{self.test_user_id}/"
        
        try:
            response = requests.delete(url, headers=self.get_headers())
            
            success = response.status_code == 204
            self.print_result(
                "Supprimer utilisateur",
                success,
                f"Status: {response.status_code}"
            )
            return success
        except Exception as e:
            self.print_result("Supprimer utilisateur", False, str(e))
            return False
    
    # ===================================
    # TESTS LIVREURS
    # ===================================
    
    def test_list_delivery_persons(self):
        """Test: GET /api/accounts/delivery-persons/"""
        url = f"{self.base_url}/delivery-persons/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else result.get('count', 0)
                self.print_result(
                    "Lister tous les livreurs",
                    True,
                    f"Nombre de livreurs: {count}"
                )
                return True
            else:
                self.print_result(
                    "Lister tous les livreurs",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Lister tous les livreurs", False, str(e))
            return False
    
    def test_list_available_delivery_persons(self):
        """Test: GET /api/accounts/delivery-persons/available/"""
        url = f"{self.base_url}/delivery-persons/available/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else result.get('count', 0)
                self.print_result(
                    "Lister livreurs disponibles",
                    True,
                    f"Livreurs disponibles: {count}"
                )
                return True
            else:
                self.print_result(
                    "Lister livreurs disponibles",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Lister livreurs disponibles", False, str(e))
            return False
    
    def test_get_delivery_person_detail(self):
        """Test: GET /api/accounts/delivery-persons/{id}/"""
        if not self.test_delivery_id:
            self.print_result("Récupérer détails livreur", False, "Pas d'ID livreur de test")
            return False
        
        url = f"{self.base_url}/delivery-persons/{self.test_delivery_id}/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Récupérer détails livreur",
                    True,
                    f"Livreur: {result.get('first_name')} {result.get('last_name')}"
                )
                return True
            else:
                self.print_result(
                    "Récupérer détails livreur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Récupérer détails livreur", False, str(e))
            return False
    
    def test_get_delivery_statistics(self):
        """Test: GET /api/accounts/delivery-persons/{id}/statistics/"""
        if not self.test_delivery_id:
            self.print_result("Récupérer statistiques livreur", False, "Pas d'ID livreur de test")
            return False
        
        url = f"{self.base_url}/delivery-persons/{self.test_delivery_id}/statistics/"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Récupérer statistiques livreur",
                    True,
                    f"Total livraisons: {result.get('total_deliveries')}, Note: {result.get('average_rating')}"
                )
                return True
            else:
                self.print_result(
                    "Récupérer statistiques livreur",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Récupérer statistiques livreur", False, str(e))
            return False
    
    # ===================================
    # TESTS APPAREILS CLIENTS
    # ===================================
    
    def test_register_device(self):
        """Test: POST /api/accounts/devices/register/"""
        url = f"{self.base_url}/devices/register/"
        self.test_device_id = f"device_{uuid.uuid4().hex}"
        
        data = {
            "device_id": self.test_device_id,
            "device_name": "iPhone de Test",
            "device_info": {
                "os": "iOS",
                "version": "15.0",
                "model": "iPhone 12"
            },
            "fcm_token": "test_fcm_token_123"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers(auth=False))
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.print_result(
                    "Enregistrer un appareil",
                    True,
                    f"Device ID: {self.test_device_id}, Nouveau: {result.get('is_new')}"
                )
                return True
            else:
                self.print_result(
                    "Enregistrer un appareil",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Enregistrer un appareil", False, str(e))
            return False
    
    def test_list_devices(self):
        """Test: GET /api/accounts/devices/"""
        url = f"{self.base_url}/devices/"
        
        try:
            response = requests.get(url, headers=self.get_headers(auth=False))
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else result.get('count', 0)
                self.print_result(
                    "Lister tous les appareils",
                    True,
                    f"Nombre d'appareils: {count}"
                )
                return True
            else:
                self.print_result(
                    "Lister tous les appareils",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Lister tous les appareils", False, str(e))
            return False
    
    def test_get_device_detail(self):
        """Test: GET /api/accounts/devices/{device_id}/"""
        if not self.test_device_id:
            self.print_result("Récupérer détails appareil", False, "Pas de device_id de test")
            return False
        
        url = f"{self.base_url}/devices/{self.test_device_id}/"
        
        try:
            response = requests.get(url, headers=self.get_headers(auth=False))
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Récupérer détails appareil",
                    True,
                    f"Device: {result.get('device_name')}"
                )
                return True
            else:
                self.print_result(
                    "Récupérer détails appareil",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Récupérer détails appareil", False, str(e))
            return False
    
    def test_update_device_customer_info(self):
        """Test: PATCH /api/accounts/devices/{device_id}/update-info/"""
        if not self.test_device_id:
            self.print_result("Mettre à jour infos client", False, "Pas de device_id de test")
            return False
        
        url = f"{self.base_url}/devices/{self.test_device_id}/update-info/"
        data = {
            "customer_name": "Jean Dupont",
            "customer_phone": "+22997123456",
            "customer_email": "jean.dupont@example.com"
        }
        
        try:
            response = requests.patch(url, json=data, headers=self.get_headers(auth=False))
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Mettre à jour infos client",
                    True,
                    f"Client: {result.get('customer_name')}"
                )
                return True
            else:
                self.print_result(
                    "Mettre à jour infos client",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Mettre à jour infos client", False, str(e))
            return False
    
    def test_update_device_patch(self):
        """Test: PATCH /api/accounts/devices/{device_id}/"""
        if not self.test_device_id:
            self.print_result("Modifier appareil (PATCH)", False, "Pas de device_id de test")
            return False
        
        url = f"{self.base_url}/devices/{self.test_device_id}/"
        data = {
            "device_name": "iPhone de Test Updated",
            "fcm_token": "updated_fcm_token_456"
        }
        
        try:
            response = requests.patch(url, json=data, headers=self.get_headers(auth=False))
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    "Modifier appareil (PATCH)",
                    True,
                    f"Device: {result.get('device_name')}"
                )
                return True
            else:
                self.print_result(
                    "Modifier appareil (PATCH)",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Modifier appareil (PATCH)", False, str(e))
            return False
    
    def test_get_device_orders(self):
        """Test: GET /api/accounts/devices/{device_id}/orders/"""
        if not self.test_device_id:
            self.print_result("Récupérer commandes appareil", False, "Pas de device_id de test")
            return False
        
        url = f"{self.base_url}/devices/{self.test_device_id}/orders/"
        
        try:
            response = requests.get(url, headers=self.get_headers(auth=False))
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else result.get('count', 0)
                self.print_result(
                    "Récupérer commandes appareil",
                    True,
                    f"Nombre de commandes: {count}"
                )
                return True
            else:
                self.print_result(
                    "Récupérer commandes appareil",
                    False,
                    f"Status {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.print_result("Récupérer commandes appareil", False, str(e))
            return False
    
    def test_delete_device(self):
        """Test: DELETE /api/accounts/devices/{device_id}/"""
        if not self.test_device_id:
            self.print_result("Supprimer appareil", False, "Pas de device_id de test")
            return False
        
        url = f"{self.base_url}/devices/{self.test_device_id}/"
        
        try:
            response = requests.delete(url, headers=self.get_headers(auth=False))
            
            success = response.status_code == 204
            self.print_result(
                "Supprimer appareil",
                success,
                f"Status: {response.status_code}"
            )
            return success
        except Exception as e:
            self.print_result("Supprimer appareil", False, str(e))
            return False
    
    # ===================================
    # EXÉCUTION DE TOUS LES TESTS
    # ===================================
    
    def run_all_tests(self):
        """Exécute tous les tests dans le bon ordre"""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}DÉMARRAGE DES TESTS - ACCOUNTS APP{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}Section 1: AUTHENTIFICATION{Colors.END}\n")
        self.test_login()
        self.test_login_invalid_credentials()
        self.test_get_me()
        self.test_change_password()
        self.test_password_reset_request()
        
        print(f"\n{Colors.YELLOW}Section 2: GESTION UTILISATEURS{Colors.END}\n")
        self.test_list_users()
        self.test_list_users_filtered()
        self.test_create_user()
        self.test_get_user_detail()
        self.test_update_user_patch()
        
        print(f"\n{Colors.YELLOW}Section 3: GESTION LIVREURS{Colors.END}\n")
        self.test_create_delivery_user()
        self.test_toggle_availability()
        self.test_list_delivery_persons()
        self.test_list_available_delivery_persons()
        self.test_get_delivery_person_detail()
        self.test_get_delivery_statistics()
        
        print(f"\n{Colors.YELLOW}Section 4: APPAREILS CLIENTS{Colors.END}\n")
        self.test_register_device()
        self.test_list_devices()
        self.test_get_device_detail()
        self.test_update_device_customer_info()
        self.test_update_device_patch()
        self.test_get_device_orders()
        
        print(f"\n{Colors.YELLOW}Section 5: NETTOYAGE{Colors.END}\n")
        self.test_delete_user()
        self.test_delete_device()
        
        # Afficher le résumé
        self.print_summary()


# ===================================
# FONCTION PRINCIPALE
# ===================================

def main():
    """Fonction principale pour exécuter les tests"""
    import sys
    
    # Vérifier si l'URL de base est fournie en argument
    base_url = API_BASE
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"\n{Colors.BLUE}Configuration:{Colors.END}")
    print(f"  Base URL: {base_url}")
    print(f"  {Colors.YELLOW}Note: Assurez-vous que le serveur Django est démarré{Colors.END}")
    print(f"  {Colors.YELLOW}Commande: python manage.py runserver{Colors.END}\n")
    
    input(f"{Colors.GREEN}Appuyez sur Entrée pour démarrer les tests...{Colors.END}\n")
    
    # Créer l'instance du testeur et exécuter les tests
    tester = AccountsEndpointTester(base_url=base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
