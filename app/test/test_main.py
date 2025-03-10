import os
import sys
import shutil
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

# Ajout du chemin du projet pour l'import correct des modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # Import correct du module principal

print(os.getcwd())  # Debugging: affiche le chemin de travail actuel

class TestMainApp(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
        # Création des dossiers de test si nécessaire
        os.makedirs("./backend/uploads", exist_ok=True)
        os.makedirs("./backend/FAISS", exist_ok=True)

    def tearDown(self):
        """Nettoyage de l'environnement après les tests"""
        if os.path.exists("./backend/uploads/test.txt"):
            os.remove("./backend/uploads/test.txt")
        if os.path.exists("./backend/uploads"):
            shutil.rmtree("./backend/uploads")

    def test_home_redirect_when_not_logged_in(self):
        """Test que la page d'accueil redirige vers login si non authentifié"""
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 307)  # Redirection temporaire
        self.assertEqual(response.headers["location"], "/login")

    def test_login_page(self):
        """Test que la page de connexion se charge correctement"""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        # Vérification des éléments du formulaire
        self.assertIn(b'<form method="post" action="/login">', response.content)
        self.assertIn(b'<input type="email"', response.content)
        self.assertIn(b'<input type="password"', response.content)

    @patch('main.login_user')
    def test_login_post_success(self, mock_login):
        """Test d'une tentative de connexion réussie"""
        mock_login.return_value = "test@example.com"
        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "password"},
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)  # Redirection après connexion réussie
        self.assertEqual(response.headers["location"], "/")

    @patch('main.login_user')
    def test_login_post_failure(self, mock_login):
        """Test d'une tentative de connexion échouée"""
        mock_login.return_value = None
        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "wrong_password"}
        )
        self.assertEqual(response.status_code, 200)  # Reste sur la page login
        self.assertIn(b"Log In", response.content)

    def test_chat_without_auth(self):
        """Test que l'accès au chat nécessite une authentification"""
        response = self.client.get("/chat", follow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/login")

    @patch('backend.database.query_data.query_database_agent')
    def test_chat_post(self, mock_query):
        """Test du chat avec authentification"""
        # Mock de la réponse de `query_database_agent`
        mock_query.return_value = "Mocked response from Gemini"

        # Définition des cookies d'authentification
        self.client.cookies.set("user", "test@example.com")
        self.client.cookies.set("session_id", "test-session")

        # Envoi de la requête POST avec JSON (important pour FastAPI)
        response = self.client.post(
            "/chat",
            json={"question": "test question"},
        )

        # Vérification du statut et du contenu
        self.assertEqual(response.status_code, 303)  # Redirection après envoi
        self.assertIn("/chat", response.headers["location"])  # Redirection vers /chat

    @patch('main.upload_doc')
    def test_upload_endpoint(self, mock_upload):
        """Test du téléversement de fichiers"""
        mock_upload.return_value = "File 'test.txt' uploaded and processed successfully."

        # Simulation de l'authentification
        self.client.cookies.set("user", "test@example.com")

        # Création du fichier de test
        test_content = b"Test content"
        response = self.client.post(
            "/upload",
            files={"file": ("test.txt", test_content, "text/plain")}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div class="alert alert-info">', response.content)
        self.assertIn(b"File &#39;test.txt&#39; uploaded and processed successfully.", response.content)

    def test_logout(self):
        """Test de la déconnexion"""
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)  # Redirection vers /login après déconnexion
        self.assertEqual(response.headers["location"], "/login")

if __name__ == '__main__':
    unittest.main()
