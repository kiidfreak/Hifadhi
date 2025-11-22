"""
Complete PayLink integration for M-Pesa and mobile money payments
Handles STK Push, payment verification, and webhook processing
"""

import os
import logging
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import hmac
import sqlite3

logger = logging.getLogger(__name__)

# ============================================
# PAYLINK CONFIGURATION
# ============================================

PAYLINK_CONFIG = {
    "api_url": os.getenv("PAYLINK_API_URL", "https://api.paylink.ke/v1"),
    "api_key": os.getenv("PAYLINK_API_KEY", ""),
    "api_secret": os.getenv("PAYLINK_API_SECRET", ""),
    "webhook_secret": os.getenv("PAYLINK_WEBHOOK_SECRET", ""),
    "callback_url": os.getenv("PAYLINK_CALLBACK_URL", "https://api.hifadhi.ai/webhooks/paylink"),
    "timeout": 30,
    "retry_attempts": 3
}


# ============================================
# MPESA STK PUSH
# ============================================

def initiate_mpesa_stk_push(
    candidate_id: str,
    amount: float,
    phone_number: str,
    payment_type: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiate M-Pesa STK Push payment
    
    Args:
        candidate_id: Candidate receiving payment
        amount: Amount in KES
        phone_number: M-Pesa phone number (254XXXXXXXXX format)
        payment_type: Type of payment (salary, bonus, reimbursement)
        description: Optional payment description
    
    Returns:
        Dictionary with transaction details
    """
    logger.info(f"💰 Initiating M-Pesa STK Push: {amount} KES to {phone_number}")
    
    # Validate and format phone number
    phone_number = _format_phone_number(phone_number)
    
    if not phone_number:
        return {
            "success": False,
            "error": "Invalid phone number format. Use 254XXXXXXXXX or 07XXXXXXXX",
            "status": "failed"
        }
    
    # Generate unique reference
    reference = f"{payment_type.upper()}_{candidate_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Prepare payload
    payload = {
        "phone_number": phone_number,
        "amount": float(amount),
        "reference": reference,
        "description": description or f"{payment_type.title()} payment for {candidate_id}",
        "callback_url": PAYLINK_CONFIG["callback_url"]
    }
    
    try:
        # Call PayLink API
        response = requests.post(
            f"{PAYLINK_CONFIG['api_url']}/payments/mpesa/stk-push",
            json=payload,
            headers=_get_headers(),
            timeout=PAYLINK_CONFIG["timeout"]
        )
        
        response.raise_for_status()
        result = response.json()
        
        transaction_id = result.get("transaction_id", "")
        checkout_request_id = result.get("checkout_request_id", "")
        
        logger.info(f"✅ STK Push initiated: {transaction_id}")
        
        # Log to database
        _log_payment_to_database(
            candidate_id=candidate_id,
            amount=amount,
            phone_number=phone_number,
            payment_type=payment_type,
            transaction_id=transaction_id,
            status="pending",
            reference=reference
        )
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "checkout_request_id": checkout_request_id,
            "reference": reference,
            "message": f"STK Push sent to {phone_number}. Please enter M-Pesa PIN.",
            "status": "pending",
            "amount": amount,
            "phone_number": phone_number
        }
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ PayLink API error: {e.response.status_code} - {e.response.text}")
        
        return {
            "success": False,
            "error": f"Payment service error: {e.response.text}",
            "status": "failed"
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error: {e}")
        
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status": "error"
        }
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }


# ============================================
# PAYMENT STATUS CHECK
# ============================================

def check_payment_status(transaction_id: str) -> Dict[str, Any]:
    """
    Check status of a PayLink transaction
    
    Args:
        transaction_id: PayLink transaction ID
    
    Returns:
        Transaction status details
    """
    logger.info(f"🔍 Checking payment status: {transaction_id}")
    
    try:
        response = requests.get(
            f"{PAYLINK_CONFIG['api_url']}/payments/status/{transaction_id}",
            headers=_get_headers(),
            timeout=15
        )
        
        response.raise_for_status()
        result = response.json()
        
        status = result.get("status", "unknown")
        
        logger.info(f"✅ Payment status: {status}")
        
        # Update database
        _update_payment_status(transaction_id, status, result)
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": status,
            "amount": result.get("amount"),
            "phone_number": result.get("phone_number"),
            "completed_at": result.get("completed_at"),
            "mpesa_receipt": result.get("mpesa_receipt_number"),
            "details": result
        }
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Status check failed: {e.response.status_code}")
        
        return {
            "success": False,
            "transaction_id": transaction_id,
            "status": "unknown",
            "error": "Failed to retrieve status"
        }
    
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        
        return {
            "success": False,
            "transaction_id": transaction_id,
            "status": "error",
            "error": str(e)
        }


# ============================================
# BULK PAYMENT PROCESSING
# ============================================

def process_bulk_payments(payments: list) -> Dict[str, Any]:
    """
    Process multiple payments in bulk (e.g., monthly payroll)
    
    Args:
        payments: List of payment dictionaries with keys:
                  - candidate_id
                  - amount
                  - phone_number
                  - payment_type
    
    Returns:
        Summary of bulk payment results
    """
    logger.info(f"💰 Processing bulk payments: {len(payments)} transactions")
    
    results = {
        "total": len(payments),
        "successful": 0,
        "failed": 0,
        "pending": 0,
        "transactions": []
    }
    
    for payment in payments:
        result = initiate_mpesa_stk_push(
            candidate_id=payment["candidate_id"],
            amount=payment["amount"],
            phone_number=payment["phone_number"],
            payment_type=payment.get("payment_type", "salary")
        )
        
        results["transactions"].append({
            "candidate_id": payment["candidate_id"],
            "transaction_id": result.get("transaction_id"),
            "status": result.get("status"),
            "success": result.get("success")
        })
        
        if result.get("success"):
            if result.get("status") == "pending":
                results["pending"] += 1
            else:
                results["successful"] += 1
        else:
            results["failed"] += 1
    
    logger.info(f"✅ Bulk payment complete: {results['successful']} successful, {results['failed']} failed")
    
    return results


# ============================================
# WEBHOOK HANDLING
# ============================================

def verify_webhook_signature(payload: str, signature: str) -> bool:
    """
    Verify PayLink webhook signature for security
    
    Args:
        payload: Raw webhook payload string
        signature: Signature header from request
    
    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        PAYLINK_CONFIG["webhook_secret"].encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


def handle_payment_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming payment webhook from PayLink
    
    Args:
        webhook_data: Webhook payload
    
    Returns:
        Processing result
    """
    logger.info(f"📥 Processing payment webhook: {webhook_data.get('transaction_id')}")
    
    transaction_id = webhook_data.get("transaction_id")
    status = webhook_data.get("status")
    amount = webhook_data.get("amount")
    mpesa_receipt = webhook_data.get("mpesa_receipt_number")
    
    # Update database
    _update_payment_status(transaction_id, status, webhook_data)
    
    # Trigger notifications if needed
    if status == "completed":
        _send_payment_confirmation(transaction_id, amount, mpesa_receipt)
    elif status == "failed":
        _send_payment_failure_notification(transaction_id)
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "status": status
    }


# ============================================
# HELPER FUNCTIONS
# ============================================

def _format_phone_number(phone: str) -> Optional[str]:
    """Format phone number to 254XXXXXXXXX format"""
    phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")
    
    if phone.startswith("254") and len(phone) == 12:
        return phone
    elif phone.startswith("0") and len(phone) == 10:
        return "254" + phone[1:]
    elif phone.startswith("7") and len(phone) == 9:
        return "254" + phone
    else:
        return None


def _get_headers() -> Dict[str, str]:
    """Get API request headers with authentication"""
    return {
        "Authorization": f"Bearer {PAYLINK_CONFIG['api_key']}",
        "Content-Type": "application/json",
        "X-API-Secret": PAYLINK_CONFIG['api_secret']
    }


def _log_payment_to_database(
    candidate_id: str,
    amount: float,
    phone_number: str,
    payment_type: str,
    transaction_id: str,
    status: str,
    reference: str
) -> None:
    """Log payment to database"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    payroll_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    cursor.execute("""
        INSERT INTO payroll (
            payroll_id, candidate_id, payment_type, amount,
            payment_date, payment_method, status, transaction_id, mpesa_phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payroll_id,
        candidate_id,
        payment_type,
        amount,
        datetime.now().strftime('%Y-%m-%d'),
        'M-Pesa',
        status,
        transaction_id,
        phone_number
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Payment logged: {payroll_id}")


def _update_payment_status(transaction_id: str, status: str, details: Dict) -> None:
    """Update payment status in database"""
    conn = sqlite3.connect('data/hifadhi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE payroll
        SET status = ?
        WHERE transaction_id = ?
    """, (status, transaction_id))
    
    conn.commit()
    conn.close()


def _send_payment_confirmation(transaction_id: str, amount: float, receipt: str) -> None:
    """Send payment confirmation (placeholder for SMS/email service)"""
    logger.info(f"📧 Sending payment confirmation: {receipt}")
    # TODO: Implement SMS/email notification here


def _send_payment_failure_notification(transaction_id: str) -> None:
    """Send payment failure notification"""
    logger.info(f"⚠️ Sending payment failure notification: {transaction_id}")
    # TODO: Implement notification here


# ============================================
# WALLET MANAGEMENT
# ============================================

def get_wallet_balance() -> Dict[str, Any]:
    """
    Get current PayLink wallet balance
    
    Returns:
        Wallet balance information
    """
    try:
        response = requests.get(
            f"{PAYLINK_CONFIG['api_url']}/wallet/balance",
            headers=_get_headers(),
            timeout=15
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "balance": result.get("balance", 0),
            "currency": result.get("currency", "KES"),
            "last_updated": result.get("last_updated")
        }
    
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# TESTING & VALIDATION
# ============================================

def test_paylink_connection() -> bool:
    """
    Test PayLink API connection
    
    Returns:
        True if connection successful
    """
    logger.info("🧪 Testing PayLink connection...")
    
    try:
        response = requests.get(
            f"{PAYLINK_CONFIG['api_url']}/health",
            headers=_get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ PayLink connection successful")
            return True
        else:
            logger.error(f"❌ PayLink connection failed: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ PayLink connection error: {e}")
        return False


if __name__ == "__main__":
    # Test connection
    test_paylink_connection()
    
    # Get wallet balance
    balance = get_wallet_balance()
    print(f"\n💰 Wallet Balance: {balance}")
