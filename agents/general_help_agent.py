"""
General Help Agent - Answers FAQs using vector store (ChromaDB)
"""

import logging
from typing import Dict, Any
import chromadb
from utils.llm_client import run_llm
from utils.tracing import trace_agent
from prompts.agent_prompts import GENERAL_HELP_PROMPT

logger = logging.getLogger(__name__)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")


@trace_agent
def general_help_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Answers general HR questions using FAQ knowledge base (RAG)
    
    Args:
        state: Conversation state with general query
        
    Returns:
        Updated state with FAQ-based answer
    """
    print("---GENERAL HELP AGENT---")
    logger.info("❓ General help agent started")
    
    user_query = state.get("user_input", "")
    conversation_history = state.get("conversation_history", "")
    task = state.get("task", "Answer general HR question")
    
    print(f"📋 Task: {task}")
    print(f"🔍 Retrieving FAQs from vector store...")
    
    # Step 1: Retrieve relevant FAQs
    try:
        collection = chroma_client.get_collection(name="hr_faq_collection")
        results = collection.query(
            query_texts=[user_query],
            n_results=3,
            include=["metadatas", "documents", "distances"]
        )
        
        # Format retrieved FAQs
        faq_context = ""
        if results and results.get("metadatas") and results["metadatas"][0]:
            print(f"📚 Found {len(results['metadatas'][0])} relevant FAQs")
            for i, meta in enumerate(results["metadatas"][0]):
                q = meta.get("question", "")
                a = meta.get("answer", "")
                score = results["distances"][0][i]
                faq_context += f"FAQ {i+1} (relevance: {1 - score:.2f})\nQ: {q}\nA: {a}\n\n"
        else:
            print("❌ No relevant FAQs found")
            faq_context = "No directly relevant FAQs found in knowledge base."
    
    except Exception as e:
        logger.error(f"Vector store error: {e}")
        faq_context = "Error retrieving FAQs from knowledge base."
    
    # Step 2: Generate response using retrieved context
    prompt = GENERAL_HELP_PROMPT.format(
        task=task,
        conversation_history=conversation_history,
        faq_context=faq_context
    )
    
    print("🤖 Generating FAQ-based response...")
    final_answer = run_llm(prompt)
    
    print("✅ General help agent completed")
    logger.info("✅ FAQ response generated")
    
    updated_history = (
        conversation_history 
        + f"\nGeneral Help Agent: {final_answer}"
    )
    
    return {
        "messages": [("assistant", final_answer)],
        "conversation_history": updated_history,
        "retrieved_faqs": results.get("metadatas", [])
    }
