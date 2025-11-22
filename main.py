"""
Hifadhi Multi-Agent System - Main Entry Point
"""

import logging
from typing import Dict, Any
from datetime import datetime
from utils.tracing import setup_observability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hifadhi.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_query(query: str) -> Dict[str, Any]:
    """
    Execute a query through the Hifadhi multi-agent system
    
    Args:
        query: User's HR-related question
    
    Returns:
        Final state with response
    """
    from workflows.langgraph_workflow import app
    
    # Initialize state
    initial_state = {
        "n_iteration": 0,
        "messages": [],
        "user_input": query,
        "user_intent": "",
        "candidate_id": "",
        "job_id": "",
        "application_id": "",
        "claim_id": "",
        "next_agent": "supervisor_agent",
        "extracted_entities": {},
        "database_lookup_result": {},
        "requires_human_escalation": False,
        "escalation_reason": "",
        "billing_amount": None,
        "payment_method": None,
        "billing_frequency": None,
        "invoice_date": None,
        "conversation_history": f"User: {query}",
        "task": "Help user with their HR query",
        "final_answer": "",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n{'='*70}")
    print(f"HIFADHI MULTI-AGENT SYSTEM")
    print(f"{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}\n")
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    # Display result
    print("\n" + "="*70)
    print("FINAL RESPONSE")
    print("="*70)
    final_answer = final_state.get("final_answer", "No response generated.")
    print(final_answer)
    print("="*70 + "\n")
    
    return final_state


def interactive_mode():
    """Run in interactive mode for testing"""
    
    # Setup Observability
    print("🔭 Initializing Phoenix Observability...")
    phoenix_url = setup_observability()
    if phoenix_url:
        print(f"✅ Phoenix running at: {phoenix_url}")
    else:
        print("⚠️ Observability disabled")

    print("\n🤖 Hifadhi Interactive Mode")
    print("Type 'exit' to quit\n")
    
    while True:
        query = input("HR Manager: ")
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("Goodbye! 👋")
            break
        
        if not query.strip():
            continue
        
        try:
            run_query(query)
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run single query from command line
        # Note: Observability might not capture much in single-shot CLI mode unless we keep process alive,
        # but for now we just run it.
        query = " ".join(sys.argv[1:])
        run_query(query)
    else:
        # Interactive mode
        interactive_mode()
