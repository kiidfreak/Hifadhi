"""
Test PayLink Integration
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.paylink_tools import process_mpesa_payment, check_payment_status

class TestPayLinkIntegration(unittest.TestCase):
    
    @patch('tools.paylink_tools.requests.post')
    def test_process_mpesa_payment_success(self, mock_post):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transaction_id": "TRX123456789",
            "status": "pending",
            "message": "STK Push sent"
        }
        mock_post.return_value = mock_response
        
        # Test payment processing
        result = process_mpesa_payment(
            candidate_id="CAND001",
            amount=50000,
            phone_number="0115567694",
            payment_type="salary"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["transaction_id"], "TRX123456789")
        self.assertEqual(result["status"], "pending")
        
        # Verify API call arguments
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("payments/mpesa/stk-push", args[0])
        self.assertEqual(kwargs["json"]["amount"], 50000)
        self.assertEqual(kwargs["json"]["phone_number"], "254712345678") # Should format number

    @patch('tools.paylink_tools.requests.post')
    def test_process_mpesa_payment_failure(self, mock_post):
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid phone number"
        mock_post.return_value = mock_response
        
        result = process_mpesa_payment(
            candidate_id="CAND001",
            amount=50000,
            phone_number="0712345678",
            payment_type="salary"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid phone number", result["error"])

    @patch('tools.paylink_tools.requests.get')
    def test_check_payment_status(self, mock_get):
        # Mock status check response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transaction_id": "TRX123456789",
            "status": "completed",
            "amount": 50000
        }
        mock_get.return_value = mock_response
        
        result = check_payment_status("TRX123456789")
        
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["amount"], 50000)

if __name__ == '__main__':
    unittest.main()
