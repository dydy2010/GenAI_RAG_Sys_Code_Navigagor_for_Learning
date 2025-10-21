---
editor_options: 
  markdown: 
    wrap: 72
---

# CodeRAG: The AI-Powered Code Navigator for Data Science Students

**CodeRAG** is an intelligent code navigation system designed to help
developers and data science students understand complex personal
educational codebases. It uses Retrieval-Augmented Generation (RAG)
architecture, this tool allows users to ask questions about source code
in natural language and receive accurate, context-aware answers grounded
in the study materials.

------------------------------------------------------------------------

## 🚀 The Problem

Navigating a large, messy learning materials for coding is a major
challenge for students. After sememsters,it becomes difficult to search
for the exact code or lecture related to the knowledge point. Current
LLMs like Chatgpt cannot take in all the files and find precise
university specific context in lectures.

Students could waste time manually piecing together information, slowing
down learning.

## ✨ Our Solution: CodeRAG

CodeRAG solves this problem by providing a conversational interface to
your codebase. Instead of manually searching, you can simply **ask**.

Our system works in two main phases:

1.  **Collecting:** Scans your defined directory and collect all the
    files that you want to include into studying.

2.  **Indexing:** The entire codebase (including `.py`, `.ipynb`, `.md`,
    and other files) is parsed, broken into chunks, converted into
    vector embeddings. This creates a database stored in a FAISS vector
    database.

3.  **Query and Generation:** When you ask a question, CodeRAG finds the
    most relevant code chunks from the knowledge base and feeds them,
    along with your question, to a Large Language Model (LLM). The LLM
    then generates a comprehensive answer based *specifically* on the
    provided code context. It can work locally with llms like ollama
    models.

4.  **Evaluation:** As part of our educational journey, we developed a
    Ragas system to test our RAG performence on metrics like
    faithfullness and accuracy.

## 🛠️ Project Architecture

The project is organized into several key modules, reflecting a complete
RAG pipeline from data ingestion to user interaction.

| Module | Scripts |
|-------------------------------  | ------------------------------------------ |
| **1.Learning Files Collection** | `data_collection.py`                       |
| **2.Indexing Engine**           | `preprocessing.py`, `database.py`          |
| **3. RAG Core**                 | `rag_system.py`, or `rag_system_2.py`      |
| **4. Evaluation**               | `evaluate_ragas.py`,`Evaluation_Dataset.py`|
|                                 | `setup_for_eval.sh` , `check_eval.py`      |
|                                 | `evaluation_only_rag_sys.py`               |
| **5. User Interface**           | `streamlit_app.py`, `interface.py`         |

------------------------------------------------------------------------

## 🔧 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

-   Python
-   Ollama (for local LLM hosting)
-   An OpenAI API key (for the evaluation script) \*. setup_for_eval.sh
    specifically for the evaluation, and check_eval.py to check if setup
    is done for eval.
-   And other imports in scripts.

### Installation

1.  **Clone the repository:**
    `bash     git clone https://github.com/dydy2010/GenAI_RAG_Sys_Code_Navigagor_for_Learning.git     cd GenAI_RAG_Sys_Code_Navigagor_for_Learning`

2.  **Install dependencies:** It is recommended to use a virtual
    environment.
    `` bash     python -m venv venv     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`     pip install -r requirements.txt ``

3.  **Set up Ollama:** Make sure Ollama is running and you have pulled a
    model. `bash     ollama pull llama3`

### Running the Application

1.  **Run the indexing pipeline** to create the knowledge base from a
    target repository. *(You may need to configure the target directory
    in the script first.)* `bash     python main_new/data_collection.py`

2.  **Launch the Streamlit interface:**
    `bash     streamlit run main/streamlit_app.py` Open your browser and
    navigate to the local URL provided by Streamlit.

------------------------------------------------------------------------

## 🔮 Future Work

We have identified several key areas for future improvement to make
CodeRAG even more powerful:

-   **Improve the Query:** Implement a Query Expansion module. Before
    searching, the LLM rephrases the question, generate synonyms, or
    break a complex question into several sub-questions.
-   **Post-Retrieval Re-ranking:** Introduce a re-ranking decomposition
    process: break down a complex question into simpler sub-questions.
-   **Expanded Evaluation:** Enhance our evaluation by integrating more
    metrics like **BERTScore** for comparison. And expand our template
    dataset for ragas evaluation.

------------------------------------------------------------------------

## 🤝 Authors

Cyriel Van Helleputte Sever Alin Girardin Robin Ramiro Díez-Liébana
Dongyuan Gao

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file
for details.
