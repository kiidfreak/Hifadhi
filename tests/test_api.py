"""
Integration tests for Hifadhi API Server
"""

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_server import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "online", "system": "Hifadhi Multi-Agent OS"})

    @patch('web_server.workflow_app.invoke')
    def test_chat_endpoint(self, mock_invoke):
        # Mock workflow response
        mock_invoke.return_value = {
            "final_answer": "This is a test response.",
            "session_id": "test_session_123",
            "conversation_history": "User: Hi\nAgent: This is a test response.",
            "needs_clarification": False
        }
        
        payload = {"query": "Hello", "session_id": "test_session_123"}
        response = self.client.post("/chat", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "This is a test response.")
        self.assertEqual(data["session_id"], "test_session_123")

    @patch('web_server.sqlite3.connect')
    def test_paylink_webhook(self, mock_connect):
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_connect.return_value.cursor.return_value = mock_cursor
        
        payload = {
            "transaction_id": "TRX123",
            "status": "completed",
            "amount": 500.0,
            "reference": "REF123",
            "phone_number": "254712345678",
            "timestamp": "2023-01-01T12:00:00"
        }
        
        response = self.client.post("/webhooks/paylink", json=payload)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "received"})
        
        # Verify DB update called
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        self.assertIn("UPDATE payroll", args[0])
        self.assertIn("completed", args[1])
        self.assertIn("TRX123", args[1])

if __name__ == '__main__':
    unittest.main()
