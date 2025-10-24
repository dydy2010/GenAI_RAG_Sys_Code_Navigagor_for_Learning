"""
RAG Preprocessing Module - Code and Notebook Chunking & Embedding Pipeline

This module provides a complete preprocessing pipeline for RAG (Retrieval-Augmented Generation)
systems working with code and notebook files. It handles chunking, embedding, and database
storage for Python, R, Jupyter notebooks, R Markdown, and Quarto files.

Classes:
--------
NotebookChunker:
    Handles conversion and chunking of notebook files (.ipynb, .Rmd, .qmd) into structured
    cell-based dictionaries suitable for embedding.

DataPreprocessor:
    Main orchestrator class that processes files through the complete pipeline:
    file loading → chunking → embedding → database storage.

Supported File Types:
---------------------
- .py (Python scripts)
- .R (R scripts)
- .ipynb (Jupyter notebooks)
- .Rmd (R Markdown notebooks)
- .qmd (Quarto notebooks)

Pipeline Flow:
--------------
1. Load JSON file containing parsed code/notebook content
2. Route to appropriate handler based on file extension
3. Chunk content using language-specific text splitters
4. Generate embeddings using Qwen3-Embedding-8B model
5. Write chunks and embeddings to ChromaDB vector database

Usage Example:
--------------
    from pathlib import Path
    from module.preprocessing import DataPreprocessor

    # Get paths to your parsed JSON files
    data_dir = Path("./data/parsed")
    path_files = [str(f) for f in data_dir.glob("*.json")]

    # Initialize and run preprocessor
    preprocessor = DataPreprocessor(path_files, database)
    preprocessor.prepare()

Expected JSON Input Format:
---------------------------
Each JSON file should contain:
    {
        "name": "filename_without_extension",
        "extension": ".py|.R|.ipynb|.Rmd|.qmd",
        "content": "raw file content or notebook dict",
        ...additional metadata fields...
    }

Dependencies:
-------------
- langchain_text_splitters: For language-aware code chunking
- sentence_transformers: For Qwen3-Embedding-8B embeddings
- jupytext: For .Rmd to .ipynb conversion (external CLI tool)
- quarto: For .qmd to .ipynb conversion (external CLI tool)
- module.database: Database and DatabaseWriter classes for ChromaDB operations

Notes:
------
- Chunk size is set to 50 characters (may need tuning for production)
- Embeddings are normalized by default
- Notebook conversion requires jupytext and quarto CLI tools installed
- Temporary files are created in ./temp directory during notebook processing
- Each chunk receives the same metadata from the source file (excluding content)
"""

from pathlib import Path
import json
import itertools
import os
import subprocess
from copy import deepcopy

from module.database import Database, DatabaseWriter
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from sentence_transformers import SentenceTransformer


class NotebookChunker:
    """
    Handles conversion and cell-level chunking of notebook files.

    This class converts R Markdown (.Rmd) and Quarto (.qmd) notebooks to Jupyter
    (.ipynb) format, then extracts code and markdown cells as individual chunks
    for embedding and storage in a vector database.

    The conversion process uses external CLI tools:
    - jupytext: For .Rmd → .ipynb conversion
    - quarto: For .qmd → .ipynb conversion

    Attributes:
        file (dict): Deep copy of the input file dictionary containing name,
                     extension, and content
        rmd_to_ipynb (list[str]): Command template for jupytext conversion
        qmd_to_ipynb (list[str]): Command template for quarto conversion
        file_path (str): Full filename with extension
        path (Path): Full path to temporary file location

    Example:
        >>> file_dict = {
        ...     "name": "analysis",
        ...     "extension": ".Rmd",
        ...     "content": "# Title\\n```{r}\\nplot(1:10)\\n```"
        ... }
        >>> chunker = NotebookChunker(file_dict)
        >>> chunked = chunker.chunk()
        >>> print(chunked["content"])
        [{"markdown": "# Title"}, {"code": "plot(1:10)"}]
    """

    def __init__(self, file: dict):
        """
        Initialize the NotebookChunker with a file dictionary.

        Creates a ./temp directory if it doesn't exist, and sets up conversion
        commands for different notebook formats.

        Args:
            file (dict): Dictionary containing at minimum:
                - "name" (str): Filename without extension
                - "extension" (str): File extension (.ipynb, .Rmd, or .qmd)
                - "content" (str | dict): File content (string for .Rmd/.qmd,
                                         dict for .ipynb)
        """
        # Ensure temporary directory exists for file conversion operations
        if not os.path.exists("./temp"):
            os.mkdir("./temp")

        # Create deep copy to avoid modifying the original file dict
        self.file: dict = deepcopy(file)

        # Define CLI command templates for notebook format conversion
        # jupytext converts R Markdown to Jupyter notebook format
        self.rmd_to_ipynb: list[str] = ["jupytext", "--to", "notebook"]
        # quarto converts Quarto documents to Jupyter notebook format
        self.qmd_to_ipynb: list[str] = ["quarto", "convert"]

        # Construct full filename (name + extension)
        self.file_path: str = self.file["name"] + self.file["extension"]
        # Create full path to temporary file location
        self.path: Path = Path("./temp", self.file_path)

    def recreate(self):
        """
        Recreate the original file in the ./temp directory.

        Writes the file content to disk so it can be processed by external
        conversion tools. Handles both .ipynb files (written as JSON) and
        text-based notebooks like .Rmd and .qmd (written as plain text).

        Side Effects:
            Creates a file at ./temp/{filename}{extension}
        """
        # Check if file is already in Jupyter notebook format
        if ".ipynb" in self.file_path:
            # For .ipynb files, content is a dict that needs to be serialized as JSON
            with open(Path("./temp/", self.file_path), "w") as fp:
                json.dump(self.file["content"], fp)
        else:
            # For .Rmd and .qmd files, content is already a string
            with open(Path("./temp/", self.file_path), "w") as f:
                f.write(self.file["content"])

    def convert(self):
        """
        Convert .Rmd and .qmd files to .ipynb format using external CLI tools.

        Uses subprocess to call:
        - `jupytext --to notebook <file.Rmd>` for R Markdown files
        - `quarto convert <file.qmd>` for Quarto files

        For .ipynb files, no conversion is performed.

        Side Effects:
            - Creates a .ipynb file in the ./temp directory
            - Prints conversion status messages to stdout

        Dependencies:
            - jupytext CLI tool (for .Rmd)
            - quarto CLI tool (for .qmd)
        """
        # First, recreate the file in the temp directory
        self.recreate()

        # Handle Quarto document conversion
        if self.file["extension"] == ".qmd":
            # Create a copy of the base command to avoid modifying the template
            cmd: list[str] = deepcopy(self.qmd_to_ipynb)
            # Append the file path to convert
            cmd.append(str(self.path))
            # Execute the quarto conversion command
            result = subprocess.run(cmd)
            # Check conversion result (note: logic seems inverted)
            if not result:
                print("Conversion successful!")
            else:
                print(f"Could not convert '{self.path}'")

        # Handle R Markdown conversion
        elif self.file["extension"] == ".Rmd":
            # Create a copy of the base command to avoid modifying the template
            cmd: list[str] = deepcopy(self.rmd_to_ipynb)
            # Append the file path to convert
            cmd.append(str(self.path))
            # Execute the jupytext conversion command
            result = subprocess.run(cmd)
            # Check conversion result (note: logic seems inverted)
            if not result:
                print("Conversion successful!")
            else:
                print(f"Could not convert '{self.path}'")

        # No conversion needed for .ipynb files
        else:
            print("File is already a '.ipynb' file. No need for conversion.")

    def remove_temp(self) -> None:
        """
        Remove temporary files created during conversion.

        Note: Current implementation attempts to remove ./temp directory,
              but should likely remove individual temp files instead.
        """
        os.remove("./temp")

    def chunk(self):
        """
        Convert notebook to .ipynb format and extract cells as individual chunks.

        This is the main method that orchestrates the chunking process:
        1. Converts the notebook to .ipynb format (if needed)
        2. Loads the resulting .ipynb file
        3. Extracts code and markdown cells
        4. Formats each cell as {cell_type: content} dictionary
        5. Replaces the file's content with the list of cell dictionaries

        Returns:
            dict: The modified file dictionary with "content" now containing
                  a list of cell dictionaries in the format:
                  [{"code": "..."}, {"markdown": "..."}, ...]
        """
        # Construct path to the converted .ipynb file
        # (conversion changes extension but keeps the name)
        notebook_path: str = str(Path("./temp", self.file["name"] + ".ipynb"))

        # Convert the file to .ipynb format (handles .Rmd, .qmd, and .ipynb)
        self.convert()

        # Open and parse the converted Jupyter notebook
        with open(notebook_path, "r") as f:
            notebook: dict = json.load(f)

            # Extract cell content from the notebook structure
            # Each cell becomes a dict with cell_type as key and joined source as value
            content: list[dict] = [
                # Create dict with cell type (code/markdown) as key
                {cell["cell_type"]: "".join(cell["source"])}
                # Iterate through all cells in the notebook
                for cell in notebook["cells"]
                # Only include code and markdown cells (skip raw, etc.)
                if cell["cell_type"] in ["code", "markdown"]
            ]

        # Replace the original content with the list of cell dictionaries
        self.file["content"] = content
        return self.file


class DataPreprocessor:
    """
    Main orchestrator for the RAG preprocessing pipeline.

    This class manages the complete preprocessing workflow for multiple files:
    - Loads JSON files containing parsed code/notebook content
    - Routes files to appropriate handlers based on extension
    - Chunks content using language-specific text splitters
    - Generates embeddings using the Qwen3-Embedding-8B model
    - Writes chunks and embeddings to ChromaDB vector database

    The class uses a shared counter across all instances to generate unique
    IDs for database records.

    Attributes:
        count (itertools.count): Class-level counter for generating unique IDs
        qwen_embedding (SentenceTransformer): Embedding model instance
        path_files (list[str]): List of file paths to process
        python_splitter (RecursiveCharacterTextSplitter): Python-aware text splitter
        r_splitter (RecursiveCharacterTextSplitter): Generic text splitter for R
        writer (DatabaseWriter): Database writer for ChromaDB operations

    Example:
        >>> from pathlib import Path
        >>> files = [str(p) for p in Path("./data/parsed").glob("*.json")]
        >>> preprocessor = DataPreprocessor(files, database)
        >>> preprocessor.prepare()  # Process all files
    """

    # Class-level counter shared across all instances for unique ID generation
    # Starts at 0 and increments with each next() call
    count = itertools.count(0)

    def __init__(self, path_files: list[str], database: Database):
        """
        Initialize the DataPreprocessor with file paths and required components.

        Sets up:
        - Qwen3-Embedding-8B model for generating embeddings
        - Language-specific text splitters for chunking
        - Database connection and writer

        Args:
            path_files (list[str]): List of paths to JSON files to process.
                                   Each file should contain parsed code/notebook data.
            database (Database): A dataclass containing the connection to the database.

        Note:
            - Chunk size is set to 50 characters (may need adjustment for production)
        """
        # Initialize the embedding model (8B parameter model from Qwen)
        # This model is optimized for both code and text retrieval tasks
        print("Loading or Downloading HuggingFace 'Qwen/Qwen3-Embedding-8B'")
        self.qwen_embedding = SentenceTransformer("Qwen/Qwen3-Embedding-8B")

        # Store the list of file paths to process
        self.path_files: list[str] = path_files

        # Initialize Python-specific text splitter
        # Language.PYTHON ensures splitting respects Python syntax boundaries
        self.python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=50,  # Maximum characters per chunk
            chunk_overlap=0,  # No overlap between adjacent chunks
        )

        # Recursively separates R file based on common paragraph separators ("\n\n", "\n")
        self.r_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=0)

        # Recursively separates text file based on common paragraph separators ("\n\n", "\n")
        # Set up a larger chunk size since we're handling PDF's
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200, chunk_overlap=30
        )

        # User

        # Create writer for the "database" collection in ChromaDB
        self.writer: DatabaseWriter = DatabaseWriter(database, "database")

    def prepare(self):
        """
        Process all files through the preprocessing pipeline.

        Main orchestration method that:
        1. Iterates through each file path
        2. Loads the JSON file
        3. Routes to the appropriate handler based on file extension
        4. Writes the resulting chunks and embeddings to the database

        Supported extensions: .py, .R, .ipynb, .Rmd, .qmd, .pdf

        Side Effects:
            - Writes records to ChromaDB vector database
            - Prints warnings for unsupported file types
            - May create temporary files in ./temp directory (for notebooks)
        """
        # Iterate through each file path in the list
        for path in self.path_files:
            # Open and load the JSON file
            with open(path, "r") as f:
                file = json.load(f)
                # Extract the file extension to determine processing route
                extension: str = file["extension"]

            # Route Python files to Python-specific handler
            if extension == ".py":
                # Process file and get database records
                records = self.python_route(file)
                # Write records to ChromaDB
                self.writer.write(**records)

            # Route R files to R-specific handler
            elif extension == ".R":
                # Process file and get database records
                records = self.r_route(file)
                # Write records to ChromaDB
                self.writer.write(**records)

            # Route notebook files to notebook-specific handler
            elif extension in [".ipynb", ".Rmd", ".qmd"]:
                # Process file and get database records
                records = self.notebook_route(file)
                # Write records to ChromaDB
                self.writer.write(**records)

            elif extension == ".pdf":
                records = self.pdf_route(file)

                self.writer.write(**records)

            # Handle unsupported file types
            else:
                print(
                    "Unknown or unsupported extension type. Please make sure that "
                    "the provided file 'extension' key is '.py', '.R', '.ipynb', "
                    "'.Rmd', or '.qmd'"
                )

    def python_route(self, file: dict) -> dict:
        """
        Process Python (.py) files: chunk, embed, and prepare database records.

        Uses Python-aware RecursiveCharacterTextSplitter that respects Python
        syntax boundaries when creating chunks.

        Args:
            file (dict): File dictionary containing "content" key with Python code

        Returns:
            dict: Database records dictionary with keys:
                - "ids_list": List of unique string IDs
                - "documents_list": List of text chunks
                - "embeddings_list": List of normalized embeddings (numpy arrays)
                - "metadatas_list": List of metadata dicts (file info minus content)
        """
        # Split Python code into chunks using syntax-aware splitter
        splitted_content = self.python_splitter.split_text(file["content"])

        # Generate normalized embeddings for each chunk
        # normalize_embeddings=True scales vectors to unit length for cosine similarity
        embeddings = self.qwen_embedding.encode(
            splitted_content, normalize_embeddings=True
        )

        # Construct database records dictionary
        records = {
            # Generate unique sequential IDs for each chunk
            "ids_list": [str(next(self.count)) for _ in range(len(splitted_content))],
            # The text chunks themselves
            "documents_list": splitted_content,
            # The embedding vectors for each chunk
            "embeddings_list": embeddings,
            # Metadata for each chunk (all file fields except content)
            # Each chunk gets a copy of the same metadata
            "metadatas_list": [
                {k: v for k, v in file.items() if k != "content"}
                for _ in range(len(splitted_content))
            ],
        }
        return records

    def r_route(self, file: dict) -> dict:
        """
        Process R (.R) files: chunk, embed, and prepare database records.

        Uses generic RecursiveCharacterTextSplitter for R code chunking.

        Args:
            file (dict): File dictionary containing "content" key with R code

        Returns:
            dict: Database records dictionary with keys:
                - "ids_list": List of unique string IDs
                - "documents_list": List of text chunks
                - "embeddings_list": List of normalized embeddings (numpy arrays)
                - "metadatas_list": List of metadata dicts (file info minus content)
        """
        # Split R code into chunks using generic text splitter
        splitted_content = self.r_splitter.split_text(file["content"])

        # Generate normalized embeddings for each chunk
        embeddings = self.qwen_embedding.encode(
            splitted_content, normalize_embeddings=True
        )

        # Construct database records dictionary (same structure as python_route)
        records = {
            # Generate unique sequential IDs for each chunk
            "ids_list": [str(next(self.count)) for _ in range(len(splitted_content))],
            # The text chunks themselves
            "documents_list": splitted_content,
            # The embedding vectors for each chunk
            "embeddings_list": embeddings,
            # Metadata for each chunk (all file fields except content)
            "metadatas_list": [
                {k: v for k, v in file.items() if k != "content"}
                for _ in range(len(splitted_content))
            ],
        }
        return records

    def notebook_route(self, file: dict) -> dict:
        """
        Process notebook files: convert, chunk by cell, embed, and prepare records.

        Handles .ipynb, .Rmd, and .qmd files by:
        1. Converting to .ipynb format (if needed)
        2. Extracting cells as individual chunks
        3. Generating separate embeddings for each cell
        4. Creating database records for each cell

        Each cell (code or markdown) becomes a separate document in the database,
        all sharing the same file-level metadata.

        Args:
            file (dict): File dictionary containing notebook data

        Returns:
            dict: Database records dictionary with keys:
                - "ids_list": List of unique string IDs (one per cell)
                - "documents_list": List of cell contents
                - "embeddings_list": List of normalized embeddings (one per cell)
                - "metadatas_list": List of metadata dicts (same for all cells)

        Side Effects:
            Creates temporary files in ./temp directory during conversion
        """
        # Initialize notebook chunker to handle conversion and cell extraction
        notebook_chunker: NotebookChunker = NotebookChunker(file)

        # Convert notebook and extract cells as individual chunks
        # Returns file dict with content replaced by list of cell dicts
        splitted_file: dict = notebook_chunker.chunk()

        # Generate embeddings for each cell
        # Code cells and markdown cells are embedded separately
        embeddings = [
            # Check if current cell is a code cell
            self.qwen_embedding.encode(cell["code"], normalize_embeddings=True)
            if "code" in cell.keys()
            # Otherwise it's a markdown cell
            else self.qwen_embedding.encode(cell["markdown"], normalize_embeddings=True)
            # Iterate through all cells in the chunked notebook
            for cell in splitted_file["content"]
        ]

        # Construct database records dictionary
        records = {
            # Generate unique sequential IDs for each cell
            "ids_list": [
                str(next(self.count)) for _ in range(len(splitted_file["content"]))
            ],
            # Extract cell content from each dict (first value in each cell dict)
            # Handles both {"code": "..."} and {"markdown": "..."} formats
            "documents_list": [
                list(cell.values())[0] for cell in splitted_file["content"]
            ],
            # The embedding vectors for each cell
            "embeddings_list": embeddings,
            # Metadata for each cell (all file fields except content)
            # All cells from same notebook get identical metadata
            "metadatas_list": [
                {k: v for k, v in file.items() if k != "content"}
                for _ in range(len(splitted_file["content"]))
            ],
        }
        return records

    def pdf_route(self, file: dict) -> dict:
        """
        Process PDF (.pdf) files: chunk, embed, and prepare database records.

        Uses generic RecursiveCharacterTextSplitter with medium chunk size and overlap for text code chunking.

        Args:
            file (dict): File dictionary containing "content" key with text.

        Returns:
            dict: Database records dictionary with keys:
                - "ids_list": List of unique string IDs
                - "documents_list": List of text chunks
                - "embeddings_list": List of normalized embeddings (numpy arrays)
                - "metadatas_list": List of metadata dicts (file info minus content)
        """

        # Split pure text into chunks using text splitter.
        splitted_content = self.text_splitter.split_text(file["content"])

        # Generate normalized embeddings for each chunk
        # normalize_embeddings=True scales vectors to unit length for cosine similarity
        embeddings = self.qwen_embedding.encode(
            splitted_content, normalize_embeddings=True
        )
        records = {
            # Generate unique sequential IDs for each chunk
            "ids_list": [str(next(self.count)) for _ in range(len(splitted_content))],
            # The text chunks themselves
            "documents_list": splitted_content,
            # The embedding vectors for each chunk
            "embeddings_list": embeddings,
            # Metadata for each chunk (all file fields except content)
            "metadatas_list": [
                {k: v for k, v in file.items() if k != "content"}
                for _ in range(len(splitted_content))
            ],
        }
        return records


data_dir = Path("/Users/robingirardin/hslu/rag-code-navigator/Final/data/parsed")

path_files = [str(child) for child in data_dir.iterdir()]

pdf_files = []
for path in path_files:
    print(path)
    with open(path, "r") as f:
        file = json.load(f)

    if file["extension"] == ".pdf":
        pdf_files.append(path)
