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
# pip install openai

import os
import json
from pathlib import Path
import pandas
# Limit ragas to 2 parallel jobs to prevent system overload
os.environ["RAGAS_EVAL_THREADS"] = "1"
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
# Import the necessary LLMs for Ragas configuration (OpenAI used below)

#%% Cell 2
# 1. Import test data and set up evaluation
# ------------------------------------------------------------------
print("Setting up evaluation...")

from Evaluation_Dataset import test_questions

# Mock the RAG chain functionality for evaluation
def get_rag_response(question):
    """
    This function should be replaced with your actual RAG system's response function.
    For now, it returns a mock response.
    """
    return {
        'query': question,
        'result': f"This is a mock response to: {question}",
        'source_documents': [
            {
                'page_content': f"Context related to: {question}",
                'metadata': {'source': 'mock_source.pdf', 'page': 1}
            }
        ]
    }

print("✓ Evaluation setup complete.")

#%% Cell 3
# 2. Build responses: prefer recorded file, else generate
# ------------------------------------------------------------------
print("\nBuilding responses for evaluation...")
responses = []
resp_path = (Path(__file__).parent / "responses.json").resolve()
if resp_path.exists():
    print(f"Found recorded responses: {resp_path}. Loading...")
    with open(resp_path, 'r', encoding='utf-8') as f:
        responses = json.load(f)
else:
    print("No recorded responses.json found. Generating responses now...")
    # Use tqdm for progress bar
    for item in tqdm(test_questions, desc="Processing questions"):
        try:
            question = item["question"]
            # Get RAG response
            result = get_rag_response(question)
            
            # Extract the response and context
            response = result["result"]
            retrieved_contexts = [doc['page_content'] for doc in result["source_documents"]]
            
            # Collect the results
            responses.append({
                "question": question,
                "answer": response,
                "contexts": retrieved_contexts,
                "ground_truth": item["ground_truth"],
                "ground_truth_context": item["ground_truth_context"]
            })
        except Exception as e:
            print(f"\nError processing question '{item['question']}': {e}")
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

print("Configuring Ragas with OpenAI API...")

from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

# Use faster, cheaper model for evaluation
EVAL_LLM_MODEL = "gpt-4-turbo"  # or "gpt-5" if need higher quality

# Embedding model for RAGAS context comparisons (align with RAG system default)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# for more similar embedding model as rag core, use Qwen, if you have more powerful computer

ragas_llm = ChatOpenAI(model=EVAL_LLM_MODEL)
ragas_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

metrics = [
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
]

print("✓ Ragas configured with OpenAI API")

#%% Cell 6
# 5. Run evaluation
# ------------------------------------------------------------------
import pandas as pd
from tqdm import tqdm
import time

print("\n🚀 Starting Ragas evaluation... (True serial execution: 1 metric at a time)")

results_list = []

# Loop 1: Iterate through each question
for i in tqdm(range(len(dataset)), desc="Evaluating Questions"):
    row = dataset[i]

    # Create the single-item dataset for this row
    single_item_dataset = Dataset.from_dict({
        'question': [row['question']],
        'answer': [row['answer']],
        'contexts': [row['contexts']],
        'ground_truth': [row['ground_truth']],
        'ground_truth_context': [row['ground_truth_context']]
    })

    question_results = row.copy()  # Copy all input data (question, answer, contexts, etc.)

    # Loop 2: Iterate through each metric, one by one
    for metric in tqdm(metrics, desc=f"  Metrics Q{i+1}", leave=False):
        try:
            # Evaluate this single item with ONLY this single metric
            result = evaluate(
                single_item_dataset,
                metrics=[metric],
                llm=ragas_llm,
                embeddings=ragas_embeddings,
                raise_exceptions=False
            )

            # Extract the score - FIXED: handle potential None values
            score = result.to_pandas()[metric.name].iloc[0]
            question_results[metric.name] = float(score) if score is not None else float('nan')

        except Exception as e:
            print(f"❌ FAILED [Q{i+1}, {metric.name}]: {e}")
            question_results[metric.name] = float('nan')

        # ADD: Small delay between metrics (2-3 seconds)
        time.sleep(3)

    results_list.append(question_results)

    # Critical: Add the 10-second delay between questions
    print(f"✓ Completed Q{i+1}. Cooling down for 10s...")
    time.sleep(10)

# Combine all results
df = pd.DataFrame(results_list)
print(f"\n✅ Evaluation complete! Processed {len(df)} questions.")

# Display quick summary
if not df.empty:
    print("\n📊 Quick Summary:")
    metric_cols = [m.name for m in metrics]
    print(df[metric_cols].mean())
#%% Cell 7
# 6. Display, clean, and save the results
# ------------------------------------------------------------------
from datetime import datetime

print("\n📊 Full Evaluation Results (including any errors):\n")
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
# --- Save Results ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. Save the original clean results (the metrics summary you have now)
output_file = f"ragas_evaluation_results_{timestamp}.csv"
df_clean.to_csv(output_file, index=False)
print(f"\nClean results saved to {output_file}")

# 2. Save the new, detailed "full report" in the format you want

# Define the columns we want to rename for your format
column_rename_map = {
    "question": "user_input",
    "answer": "response",
    "contexts": "retrieved_contexts",
    "ground_truth": "reference"
}

# Create the new report by renaming columns from df_clean
df_full_report = df_clean.rename(columns=column_rename_map)

# Get all metric names
metric_cols = [m.name for m in metrics]

# Define the final desired order for your columns
desired_columns = [
    "user_input", 
    "retrieved_contexts", 
    "response", 
    "reference"
] + metric_cols

# Reorder columns (and this will also drop any extras, like 'ground_truth_context')
df_full_report = df_full_report[desired_columns]

# Save this new, detailed report to a different file
report_file = f"ragas_full_report_{timestamp}.csv"
df_full_report.to_csv(report_file, index=False)

print(f"\nFull, detailed report saved to {report_file}")
