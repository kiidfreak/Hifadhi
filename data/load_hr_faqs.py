"""
Load HR-specific FAQs into ChromaDB for General Help Agent
"""

import chromadb
import pandas as pd
from tqdm import tqdm
import os

def setup_hr_faq_vector_store():
    """Create ChromaDB collection with HR FAQs"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Sample HR FAQs (you can expand this)
    faqs = [
        {
            "question": "What documents do I need for KRA PIN verification?",
            "answer": "You need a copy of your National ID or Passport. The KRA PIN must match the name on your ID exactly."
        },
        {
            "question": "How long does the hiring process take?",
            "answer": "Our typical hiring process takes 7-14 days from application to offer, including AI screening, interviews, and background checks."
        },
        {
            "question": "What is the onboarding process?",
            "answer": "Onboarding includes document verification, compliance checks (KRA, NSSF, NHIF), contract signing, system access setup, and initial training. It typically takes 2-3 days."
        },
        {
            "question": "When will I receive my first payment?",
            "answer": "Payments are processed on the 5th of each month via M-Pesa or bank transfer. Your first payment will be prorated based on your start date."
        },
        {
            "question": "What shifts are available?",
            "answer": "We offer morning (6AM-2PM), afternoon (2PM-10PM), and night shifts (10PM-6AM). Flexibility varies by role and department."
        },
        # Add 50+ more FAQs here
    ]
    
    df_faqs = pd.DataFrame(faqs)
    df_faqs["combined"] = "Question: " + df_faqs["question"] + " \nAnswer: " + df_faqs["answer"]
    
    # Setup ChromaDB
    chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
    collection = chroma_client.get_or_create_collection(name="hr_faq_collection")
    
    # Add FAQs to collection
    batch_size = 50
    for i in tqdm(range(0, len(df_faqs), batch_size)):
        batch_df = df_faqs.iloc[i:i+batch_size]
        collection.add(
            documents=batch_df["combined"].tolist(),
            metadatas=[{"question": q, "answer": a} for q, a in zip(batch_df["question"], batch_df["answer"])],
            ids=batch_df.index.astype(str).tolist()
        )
    
    print(f"✅ Loaded {len(df_faqs)} FAQs into vector store")
    return collection


if __name__ == "__main__":
    setup_hr_faq_vector_store()
