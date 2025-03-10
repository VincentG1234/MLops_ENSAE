import os
import sys
import unittest
from unittest.mock import Mock, patch, mock_open
import numpy as np
import json

# Ajoute app/ et MLops_ENSAE/ au chemin d'import
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.query_data import query_database_agent
class TestQueryData(unittest.TestCase):
    def setUp(self):
        """Configuration initiale avant chaque test"""
        self.mock_faiss = Mock()
        self.mock_gemini = Mock()
        self.mock_encode = Mock()
        self.mock_open = mock_open(read_data=json.dumps(["Chunk 1", "Chunk 2", "Chunk 3"]))

    @patch('backend.database.query_data.open', new_callable=mock_open, create=True)  # Mock `open()` pour chunks.json
    @patch('backend.database.query_data.faiss.read_index')  # Mock FAISS
    @patch('backend.database.query_data.genai.GenerativeModel')  # Mock Gemini
    @patch('backend.database.query_data.encode')  # Mock MiniLM v6 (Hugging Face)
    def test_query_database_agent(self, mock_encode, mock_gemini, mock_faiss, mock_file):
        """Test de la fonction query_database_agent"""

        # 🟢 Mock du fichier chunks.json
        mock_file.return_value = self.mock_open()

        # 🟢 Mock FAISS index
        mock_faiss_instance = Mock()
        mock_faiss_instance.search.return_value = (np.array([[0.1, 0.2, 0.3]]), np.array([[0, 1, 2]]))
        mock_faiss.return_value = mock_faiss_instance

        # 🟢 Mock l'encodage avec MiniLM v6
        mock_encode.return_value = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)

        # 🟢 Mock Gemini API
        mock_gemini_instance = Mock()
        mock_gemini_instance.generate_content.return_value = Mock(text="Mocked Gemini response")
        mock_gemini.return_value = mock_gemini_instance

        # 🟢 Exécution de la fonction avec des paramètres fictifs
        response = query_database_agent(query_text="test question")

        # 🛠️ Vérifications
        self.assertEqual(response, "Mocked Gemini response")  # Vérifie la réponse de Gemini
        mock_encode.assert_called_once_with("test question", None, None)  # Vérifie l'encodage avec MiniLM v6
        mock_faiss_instance.search.assert_called_once()  # Vérifie la recherche KNN avec FAISS
        mock_gemini_instance.generate_content.assert_called_once()  # Vérifie que Gemini est bien appelé une seule fois
        mock_file.assert_called_once_with("./backend/FAISS/chunks.json", "r")  # Vérifie l'ouverture correcte du fichier chunks.json

        print("✅ Test passé : query_database_agent fonctionne correctement avec FAISS, MiniLM et Gemini, et charge bien chunks.json.")

if __name__ == '__main__':
    unittest.main()
