"""
PayLink integration for M-Pesa payments
"""

import logging
import requests
import json
from typing import Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

PAYLINK_API_URL = os.getenv("PAYLINK_API_URL", "https://api.paylink.ke/v1")
PAYLINK_API_KEY = os.getenv("PAYLINK_API_KEY", "")


def process_mpesa_payment(
    candidate_id: str,
    amount: float,
    phone_number: str,
    payment_type: str
) -> Dict[str, Any]:
    """
    Process M-Pesa payment via PayLink API
    
    Args:
        candidate_id: Candidate receiving payment
        amount: Payment amount in KES
        phone_number: M-Pesa registered phone (format: 254712345678)
        payment_type: Type of payment (salary, bonus, reimbursement)
    
    Returns:
        Payment transaction result
    """
    logger.info(f"💰 Processing M-Pesa payment: {amount} KES to {phone_number}")
    
    # Validate phone number format
    if not phone_number.startswith("254"):
        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]
        else:
            phone_number = "254" + phone_number
    
    # Prepare payment payload
    payload = {
        "phone_number": phone_number,
        "amount": amount,
        "reference": f"{payment_type.upper()}_{candidate_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": f"{payment_type.title()} payment for candidate {candidate_id}",
        "callback_url": f"{os.getenv('BASE_URL', 'https://api.hifadhi.ai')}/webhooks/paylink"
    }
    
    try:
        # Call PayLink API
        response = requests.post(
            f"{PAYLINK_API_URL}/payments/mpesa/stk-push",
            json=payload,
            headers={
                "Authorization": f"Bearer {PAYLINK_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            transaction_id = result.get("transaction_id", "")
            
            logger.info(f"✅ Payment initiated: {transaction_id}")
            
            # Log to database
            _log_payment_to_db(
                candidate_id=candidate_id,
                amount=amount,
                phone_number=phone_number,
                payment_type=payment_type,
                transaction_id=transaction_id,
                status="pending"
            )
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "message": f"STK Push sent to {phone_number}. Amount: KES {amount}",
                "status": "pending"
            }
        else:
            logger.error(f"❌ Payment failed: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"Payment failed: {response.text}",
                "status": "failed"
            }
    
    except Exception as e:
        logger.error(f"❌ Payment exception: {e}")
        return {
            "success": False,
            "error": str(e),
            "status": "error"
        }


def check_payment_status(transaction_id: str) -> Dict[str, Any]:
    """
    Check status of a PayLink transaction
    
    Args:
        transaction_id: Transaction ID to check
    
    Returns:
        Transaction status details
    """
    logger.info(f"🔍 Checking payment status: {transaction_id}")
    
    try:
        response = requests.get(
            f"{PAYLINK_API_URL}/payments/status/{transaction_id}",
            headers={
                "Authorization": f"Bearer {PAYLINK_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            
            logger.info(f"✅ Payment status: {status}")
            
            return {
                "transaction_id": transaction_id,
                "status": status,
                "amount": result.get("amount"),
                "phone_number": result.get("phone_number"),
                "completed_at": result.get("completed_at"),
                "details": result
            }
        else:
            logger.error(f"❌ Status check failed: {response.status_code}")
            return {
                "transaction_id": transaction_id,
                "status": "unknown",
                "error": "Failed to retrieve status"
            }
    
    except Exception as e:
        logger.error(f"❌ Status check exception: {e}")
        return {
            "transaction_id": transaction_id,
            "status": "error",
            "error": str(e)
        }


def _log_payment_to_db(
    candidate_id: str,
    amount: float,
    phone_number: str,
    payment_type: str,
    transaction_id: str,
    status: str
) -> None:
    """Log payment to database"""
    import sqlite3
    from datetime import datetime
    
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
    
    logger.info(f"✅ Payment logged to database: {payroll_id}")


def get_paylink_balance() -> Dict[str, Any]:
    """
    Get current PayLink wallet balance
    
    Returns:
        Wallet balance information
    """
    try:
        response = requests.get(
            f"{PAYLINK_API_URL}/wallet/balance",
            headers={
                "Authorization": f"Bearer {PAYLINK_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "balance": result.get("balance", 0),
                "currency": result.get("currency", "KES"),
                "last_updated": result.get("last_updated")
            }
        else:
            return {"error": "Failed to retrieve balance"}
    
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        return {"error": str(e)}
