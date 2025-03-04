import os
import shutil
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestMainApp(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
        # Create test directories if they don't exist
        os.makedirs("./uploads", exist_ok=True)
        os.makedirs("./chroma", exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        # Clean up test files and directories
        if os.path.exists("./uploads/test.txt"):
            os.remove("./uploads/test.txt")
        if os.path.exists("./uploads"):
            shutil.rmtree("./uploads")

    def test_home_redirect_when_not_logged_in(self):
        """Test that home page redirects to login when not authenticated"""
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 307)  # Temporary redirect
        self.assertEqual(response.headers["location"], "/login")

    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        # Check for login form elements instead of template name
        self.assertIn(b'<form method="post" action="/login">', response.content)
        self.assertIn(b'<input type="email"', response.content)
        self.assertIn(b'<input type="password"', response.content)

    @patch('app.main.login_user')
    def test_login_post_success(self, mock_login):
        """Test successful login attempt"""
        mock_login.return_value = "test@example.com"
        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "password"},
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)  # Redirect status
        self.assertEqual(response.headers["location"], "/")

    @patch('app.main.login_user')
    def test_login_post_failure(self, mock_login):
        """Test failed login attempt"""
        mock_login.return_value = None
        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "wrong_password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Log In", response.content)

    def test_chat_without_auth(self):
        """Test chat endpoint requires authentication"""
        response = self.client.get("/chat", follow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/login")

    @patch('app.main.query_database_agent')
    def test_chat_post(self, mock_query):
        """Test chat endpoint with authentication"""
        # Mock the response of the query_database_agent
        mock_query.return_value = {
            'answer': 'Test response',
            'sources': ['source1']
        }

        # Set up test client with authentication cookie
        self.client.cookies.set("user", "test@example.com")
        self.client.cookies.set("session_id", "test-session")

        # Make a POST request to the /chat endpoint
        response = self.client.post(
            "/chat",
            data={
                "question": "test question",
                "model_name": "gpt-4"
            }
        )

        # Verify the status code
        self.assertEqual(response.status_code, 200)

        # Check that the question is displayed
        self.assertIn(b'd-inline-block bg-primary text-white px-3 py-2 rounded-pill', response.content)
        
        # Check that the response is displayed
        self.assertIn(b'bg-light p-3 rounded-4', response.content)

        # Optionally check for sources
        self.assertIn(b'source1', response.content)


    @patch('app.main.upload_doc')
    def test_upload_endpoint(self, mock_upload):
        """Test file upload endpoint"""
        mock_upload.return_value = "File 'test.txt' uploaded and processed successfully."

        # Set authentication cookie
        self.client.cookies.set("user", "test@example.com")

        # Create test file content
        test_content = b"Test content"
        response = self.client.post(
            "/upload",
            files={"file": ("test.txt", test_content, "text/plain")}
        )

        self.assertEqual(response.status_code, 200)
        # Check for success message in alert div
        self.assertIn(b'<div class="alert alert-info">', response.content)
        self.assertIn(b"File &#39;test.txt&#39; uploaded and processed successfully.", response.content)


if __name__ == '__main__':
    unittest.main()