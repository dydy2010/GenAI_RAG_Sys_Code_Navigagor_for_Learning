# RAG Evaluation System

##  Quick Start

```bash
# 1. Setup (one time)
cd Final/Evaluation
./setup_for_eval.sh
source .venv_eval/bin/activate

# 2. Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-actual-key" > .env

# 3. First evaluation (generates + evaluates)
python3 evaluate_ragas_improved.py --generate

# 4. Future evaluations (fast! uses saved responses)
python3 evaluate_ragas_improved.py
```

**Result:** CSV file with faithfulness, answer_relevancy, context_precision, context_recall, and answer_correctness scores.

--

## Detailed Workflow

### Step 1: Environment Setup
```bash
./setup_for_eval.sh
```
This script:
1. Creates Python virtual environment (`.venv_eval`), please make sure you have python3 installed in this environment.
**Please make sure that Evaluation and Rag_core run on two different virtual environments.**
2. Installs all dependencies in correct order, if you see dependency error messsage, you can ignore and keep going. Most cases, it will not affect the final result.
3. Creates `.env` template for openai key
4. **Automatically runs `check_eval.py`** to verify installation

### Step 2: Configure API Key
Edit `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Run Evaluation
```bash
python3 evaluate_ragas.py
```

### Expected Output
```
✅ Setup complete!
🔍 Evaluating 10 questions...
[=====>] 100% (10/10)
📊 Results saved to ragas_evaluation_20251025.csv
```

## What Happens During Evaluation
1. Loads embeddings model (default: all-MiniLM-L6-v2, ~80MB) or QWEN (16GB) for encoding your questions
2. Connects to ChromaDB
3. Runs 10 test questions through mock RAG system
4. Calculates 5 metrics per question
5. Saves CSV results

### Embedding Model Options
**Default:** `sentence-transformers/all-MiniLM-L6-v2` (80MB)
- ✅ Works on most systems, light weight
- ✅ Fast download and inference
- ✅ Good quality for evaluation

**Power User Option:** `Qwen/Qwen3-Embedding-8B` (16GB)
- ⚠️ Requires 16GB+ RAM
- ⚠️ Requires powerful CPU/GPU
- ⚠️ First run downloads ~16GB
- ✅ Higher quality embeddings and consistent with rag core
- **To enable:** Uncomment line 51 in `evaluation_only_rag_sys.py`


## Sample Output
```csv
question,faithfulness,answer_relevancy,context_recall,context_precision,answer_correctness
"What is a t-test?",0.92,0.85,0.78,0.81,0.87
"Explain gradient descent",0.88,0.91,0.85,0.79,0.90
```

## Customization
- **Add more questions**: Edit `Evaluation_Dataset.py`
- **Change models**: Modify `evaluation_only_rag_sys.py`
- **Adjust metrics**: Edit `evaluate_ragas.py`

## Known Issues

We have experienced intermittent operation due to dependency conflicts. The system may run successfully for a while and then stop working. We have saved the evaluation results we obtained in CSV files in the `results/` folder. Despite the current instability, we have learned a great deal about the RAGAS evaluation framework and the challenges of dependency management in cutting-edge Evaluation projects.

## Results

The evaluation results are saved in the `results/` directory as CSV files. Each file corresponds to a run and contains the metrics computed by RAGAS.

## Outlook

We plan to continue investigating the dependency issues and improving the stability of the evaluation module in the future. We also aim to deepen our understanding of LangChain and RAGAS to build more robust evaluation pipelines. Although the current system is not running completely, the experience has provided valuable insights for future projects.
