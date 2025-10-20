"""
evaluate_ragas.py
The Theoretical Aspects of RAG Evaluation

1. There is one critical concept: The Golden Dataset. To define it:
question: A realistic question a student would ask.
ground_truth: The ideal, "perfect" answer to that question, which you write yourself based on your expert knowledge of the course material.
ground_truth_context: The specific text snippet(s) from your source documents that contain the information needed to answer the question.

2. Metrics
- Retrieval Metrics (Is it finding the right stuff?)
Context Precision: Of the documents your system found, how many were actually relevant to the question? This measures the signal-to-noise ratio. High precision means less irrelevant junk.
Context Recall: Of all the possible relevant documents, how many did the system actually find? This measures how comprehensive the retriever is.
- Generation Metrics (Is it giving a good answer?)
Faithfulness : This is the most important metric. Does the final answer stick only to the information provided in the retrieved context? If the answer includes information from the LLM's internal knowledge (or just makes things up), its faithfulness score will be low. This directly measures how well you are preventing hallucinations.
Answer Relevancy: How relevant is the final answer to the user's original question? An answer can be faithful to the context but still completely miss the point of what was asked.
Answer Correctness: How factually correct is the answer when compared to your handwritten ground_truth? This is the only metric that directly uses your ideal answer to judge the final output.

3. Library raga
https://docs.ragas.io/en/stable/
"""

#%% Cell 1
# pip install ragas pandas tqdm
# pip install -U langchain-chroma
# ollama pull phi3:medium

import os
# Limit ragas to 2 parallel jobs to prevent system overload
os.environ["RAGAS_EVAL_THREADS"] = "2"
os.environ["TOKENIZERS_PARALLELISM"] = "false" # avoid using the same tokenizer library
from datasets import Dataset
import pandas as pd
from tqdm import tqdm
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
)
# Import the necessary LLM and embedding models for Ragas configuration
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings

#%% Cell 2
# 1. Import restructured RAG_sys and test data
# ------------------------------------------------------------------
print("Importing RAG_sys_eval_only and eval dataset...")

from evaluation_only_rag_sys import setup_rag_chain, OLLAMA_MODEL, EMBEDDING_MODEL
from Evaluation_Dataset import test_questions

# Initialize the RAG chain once
qa_chain = setup_rag_chain()
print("✓ RAG chain is ready.")

#%% Cell 3
# 2. Run RAG system on the test questions with progress bar
# ------------------------------------------------------------------
print("\nRunning RAG system on test questions...")
responses = []
# Use tqdm for progress bar
for item in tqdm(test_questions, desc="Processing questions"):
    try:
        question = item["question"]
        # Get the response from your RAG chain
        result = qa_chain.invoke({"query": question})

        # Collect the results
        responses.append({
            "question": question,
            "answer": result.get("result", ""),
            "contexts": [doc.page_content for doc in result.get("source_documents", [])],
            "ground_truth": item["ground_truth"],
            # CRITICAL FIX: Changed "ground_truth_contexts" to "ground_truth_context"
            "ground_truth_context": item["ground_truth_context"]
        })
    except Exception as e:
        print(f"\nError processing question '{item['question']}': {e}")
        # Optionally, append a failed record
        responses.append({
            "question": item["question"],
            "answer": f"ERROR: {e}",
            "contexts": [],
            "ground_truth": item["ground_truth"],
            "ground_truth_context": item["ground_truth_context"]
        })

print(f"✓ Processed {len(responses)} questions.")

#%% Cell 4
# 3. Prepare the dataset for Ragas
# ------------------------------------------------------------------
print("\nPreparing dataset for Ragas evaluation...")

ragas_data = {
    "question": [item["question"] for item in responses],
    "answer": [item["answer"] for item in responses],
    "contexts": [item["contexts"] for item in responses],
    "ground_truth": [item["ground_truth"] for item in responses],
    #  Include ground_truth_context for calculating context_recall
    "ground_truth_context": [item["ground_truth_context"] for item in responses]
}
dataset = Dataset.from_dict(ragas_data)
print("✓ Dataset prepared.")
print("\nDataset structure:")
print(dataset)

#%% Cell 5
# 4. Configure Ragas with specific LLM and Embeddings
# ------------------------------------------------------------------

print("Configuring Ragas evaluators...")
# Make sure you have the model first: ollama pull phi3:medium
EVAL_LLM_MODEL = "phi3:medium" # This model is much faster, ollama gives timeout
ragas_llm = Ollama(model=EVAL_LLM_MODEL, timeout=800)

ragas_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Define metrics, now passing the configured models where necessary
metrics = [
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    # Answer correctness requires the LLM for semantic comparison
    answer_correctness,
]

#%% Cell 6
# 5. Run evaluation
# ------------------------------------------------------------------
print("\n🚀 Starting Ragas evaluation... (This can take several minutes!)")

result = evaluate(
    dataset,
    metrics=metrics,
    llm=ragas_llm,
    embeddings=ragas_embeddings
)

print("✓ Evaluation complete!")

#%% Cell 7
# 6. Display, clean, and save the results
# ------------------------------------------------------------------
from datetime import datetime

print("\n📊 Full Evaluation Results (including any errors):\n")
df = result.to_pandas()
print(df)

# Identify rows with any N/A value
is_missing = df.isna().any(axis=1)
missing_rows_count = is_missing.sum()

# Create a clean DataFrame by dropping all rows with any N/A values
df_clean = df[~is_missing] # Using boolean indexing is slightly more explicit

# --- IMPROVEMENT: Display failed rows for easier debugging ---
if missing_rows_count > 0:
    print("\n❗ Failed Evaluation Rows:\n")
    print(df[is_missing])

# --- Display clean results and mean scores ---
print("\n✨ Clean Evaluation Results (rows with errors removed):\n")
print(df_clean)

print("\n📈 Mean Scores (based on successful evaluations):\n")
# Calculate mean scores only on the clean data
if not df_clean.empty:
    print(df_clean.mean(numeric_only=True))
else:
    print("No successful evaluations to calculate mean scores.")

# --- Report on the missing values ---
if missing_rows_count > 0:
    print(f"\n⚠️ Found and removed {missing_rows_count} row(s) with missing values due to errors (e.g., timeouts).")
else:
    print("\n✅ All evaluations completed successfully with no missing values!")

# --- IMPROVEMENT: Save the clean results with a dynamic filename ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"ragas_evaluation_results_{timestamp}.csv"
df_clean.to_csv(output_file, index=False)
print(f"\nClean results saved to {output_file}")