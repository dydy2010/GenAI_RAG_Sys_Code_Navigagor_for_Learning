from pathlib import Path
from module.embedder import CodeEmbedder, TextEmbedder
from module.chunking import PyChunker, NotebookChunker, TextChunker

import json
import itertools
from module.database import Database, DatabaseWriter
from copy import deepcopy

import importlib

importlib.reload(module.database)
importlib.reload(module.chunking)
importlib.reload(module.embedder)
"""This file simulates the running pipeline recolted parsed file, chunking them, embedding them and storing them in tthe database"""

count = itertools.count(0)
directory: Path = Path("data/parsed")
paths: list[str] = [str(child) for child in directory.iterdir()]
database: Database = Database()
writer: DatabaseWriter = DatabaseWriter(database, "test")
text_embedder: TextEmbedder = TextEmbedder()
code_embedder: CodeEmbedder = CodeEmbedder()

collection = database.client.create_collection(
    name="test",
    metadata={"description": "a test collection to test whether everything works"},
)


def extend(file: dict):
    """extend the file into multiple file, one for each cell, sharing the same file metadata."""
    base = {k: v for k, v in file.items() if k != "content"}
    return [{**deepcopy(base), **cell} for cell in file.get("content", [])]


for path in paths:
    with open(path, "r") as f:
        file = json.load(f)

    # '.py' file route
    if file["extension"] == ".py":
        pychunker: PyChunker = PyChunker(file)
        chunked_file: dict = pychunker.chunk()
        documents: list[str] = chunked_file["content"]
        embeddings: list[list[float]] = code_embedder(chunked_file["content"])
        metadatas: list[dict] = [
            {k: v for k, v in chunked_file.items() if k != "content"}
            for _ in range(len(documents))
        ]
        ids: list[str] = [str(next(count)) for _ in documents]
        writer.write(
            ids_list=ids,
            documents_list=documents,
            embeddings_list=embeddings,
            metadatas_list=metadatas,
        )
    # '.R' file route
    elif file["extension"] == ".R":
        text_chunker: TextChunker = TextChunker(file)
        chunked_file: dict = text_chunker.chunk()
        documents: list[str] = chunked_file["content"]
        embeddings: list[list[float]] = text_embedder(chunked_file["content"])
        metadatas: list[dict] = [
            {k: v for k, v in chunked_file.items() if k != "content"}
            for _ in range(len(documents))
        ]
        ids: list[str] = [str(next(count)) for _ in documents]
        writer.write(
            ids_list=ids,
            documents_list=documents,
            embeddings_list=embeddings,
            metadatas_list=metadatas,
        )

    # '.Rmd' file route
    elif file["extension"] == ".Rmd":
        notebook_chunker: NotebookChunker = NotebookChunker(file)
        chunked_file: dict = notebook_chunker.chunk()
        extended: list[dict] = extend(chunked_file)
        documents: list[str] = [file["text"] for file in extended]
        embeddings: list[list[float]] = [
            text_embedder(file["text"])[0]
            if file["cell_type"] == "markdown"
            else code_embedder(file["text"])[0]
            for file in extended
        ]
        metadata: list[dict] = [
            {k: v} for k, v in file.items() for file in extended if k != "text"
        ]
        ids: list[str] = [str(next(count)) for _ in extended]
        writer.write(
            ids_list=ids,
            documents_list=documents,
            embeddings_list=embeddings,
            metadatas_list=metadata,
        )

    # '.qmd' file route
    elif file["extension"] == ".qmd":
        notebook_chunker: NotebookChunker = NotebookChunker(file)
        chunked_file: dict = notebook_chunker.chunk()
        extended: list[dict] = extend(chunked_file)
        documents: list[str] = [file["text"] for file in extended]
        embeddings: list[list[float]] = [
            text_embedder(file["text"])[0]
            if file["cell_type"] == "markdown"
            else code_embedder(file["text"])[0]
            for file in extended
        ]
        metadata: list[dict] = [
            {k: v} for k, v in file.items() for file in extended if k != "text"
        ]
        ids: list[str] = [str(next(count)) for _ in extended]
        writer.write(
            ids_list=ids,
            documents_list=documents,
            embeddings_list=embeddings,
            metadatas_list=metadata,
        )

    # '.ipynb' file route
    elif file["extension"] == ".ipynb":
        notebook_chunker: NotebookChunker = NotebookChunker(file)
        chunked_file: dict = notebook_chunker.chunk()
        extended: list[dict] = extend(chunked_file)
        documents: list[str] = [file["text"] for file in extended]
        embeddings: list[list[float]] = [
            text_embedder(file["text"])[0]
            if file["cell_type"] == "markdown"
            else code_embedder(file["text"])[0]
            for file in extended
        ]
        metadata: list[dict] = [
            {k: v} for k, v in file.items() for file in extended if k != "text"
        ]
        ids: list[str] = [str(next(count)) for _ in extended]
        writer.write(
            ids_list=ids,
            documents_list=documents,
            embeddings_list=embeddings,
            metadatas_list=metadata,
        )

    # '.pdf' file route
    elif file["extension"] == ".pdf":
        textchunker: TextChunker = TextChunker(file)
        chunked_file: dict = textchunker.chunk()
        documents: list[str] = chunked_file["content"]
        embeddings: list[list[float]] = text_embedder(chunked_file["content"])
        writer.write(
            ids_list=[str(next(count))],
            documents_list=documents,
            embeddings_list=embeddings,
            metadatas_list=[{k: v for k, v in chunked_file.items() if k != "content"}],
        )
