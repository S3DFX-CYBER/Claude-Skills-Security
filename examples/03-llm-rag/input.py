# app/assistant.py - a support assistant with retrieval and a tool call.

import os
import subprocess
import openai
from vectorstore import collection          # shared, single-namespace store

SYSTEM_PROMPT = f"""
You are Acme's support assistant. Be concise.
Internal API key for the billing lookup: {os.environ['BILLING_API_KEY']}
Internal dashboard: http://grafana.internal:3000
"""

def ingest(user_upload):
    """Add a customer-uploaded document to the knowledge base."""
    text = user_upload.read().decode('utf-8', errors='ignore')
    collection.add(documents=[text], ids=[user_upload.filename])

def answer(question, user_id):
    hits = collection.query(query_texts=[question], n_results=5)
    context = "\n\n".join(hits['documents'][0])
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content

def run_diagnostic(question, user_id):
    """Model can request a diagnostic command; we run what it returns."""
    plan = answer(question, user_id)
    if plan.startswith("DIAG:"):
        subprocess.run(plan[5:].strip(), shell=True)
