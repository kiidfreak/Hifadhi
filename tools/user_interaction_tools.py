"""
Tools for interacting with the user (clarifications, inputs)
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def ask_user(question: str, missing_info: str = "") -> Dict[str, Any]:
    """
    Prompt the user for input and return their response
    
    Args:
        question: Question to ask the user
        missing_info: Description of what information is missing
    
    Returns:
        Dictionary with user's response
    """
    logger.info(f"🗣️ Asking user: {question}")
    
    print("\n" + "="*60)
    print("---USER INPUT REQUIRED---")
    if missing_info:
        print(f"Missing: {missing_info}")
    print("="*60)
    
    answer = input(f"\n{question}\n> ")
    
    logger.info(f"✅ User responded: {answer[:100]}...")
    
    return {
        "context": answer,
        "source": "User Input",
        "timestamp": None  # Could add datetime.now()
    }


def confirm_action(action: str, details: Dict[str, Any]) -> bool:
    """
    Ask user to confirm a critical action (e.g., payment)
    
    Args:
        action: Action to confirm (e.g., "process payment")
        details: Action details to display
    
    Returns:
        True if confirmed, False otherwise
    """
    logger.info(f"⚠️ Requesting confirmation for: {action}")
    
    print("\n" + "="*60)
    print("---CONFIRMATION REQUIRED---")
    print(f"Action: {action}")
    print("\nDetails:")
    for key, value in details.items():
        print(f"  {key}: {value}")
    print("="*60)
    
    response = input("\nConfirm this action? (yes/no): ").strip().lower()
    
    confirmed = response in ["yes", "y", "confirm"]
    
    if confirmed:
        logger.info("✅ Action confirmed by user")
    else:
        logger.info("❌ Action cancelled by user")
    
    return confirmed
