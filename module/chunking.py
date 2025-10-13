import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain.core import Document


class PyChunker:
    """A class that chunks python files based on common sperator, such as 'class' or 'def'. In the file's deepcopy, replace the content by a list of splitted text."""

    def __init__(self, file: dict):
        self.file = file
        self.splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=50, chunk_overlap=0
        )

    def chunk(self):
        file_copy: dict = deepcopy(self.file)
        content: str = file_copy["content"]
        docs: list[Document] = self.splitter(content)
        documents: list[str] = [doc.text for doc in docs]

        file_copy["content"] = documents
        return file_copy


class NotebookChunker:
    """Class implementing chunking for both '.ipynb', '.qmd' and '.Rmd' file. Convert all notebook into a 'ipynb' file before replacing the file's content with a list of dictionary."""

    def __init__(self, file: dict):
        if not os.path.exists("./temp"):
            os.mkdir("./temp")

        self.file: dict = file
        self.rmd_to_ipynb: list[str] = ["jupytext", "--to", "notebook"]
        self.qmd_to_ipynb: list[str] = ["quarto", "convert"]
        self.file_path: str = self.file["name"] + self.file["extension"]
        self.path: Path = Path("./temp", self.file_path)

    def recreate(self):
        with open(Path("./temp/", self.file_path), "w") as f:
            f.write(self.file["content"])

    def convert(self):
        """Convert '.qmd' and '.Rmd' into 'ipynb'."""

        self.recreate()

        if self.file["extension"] == ".qmd":
            cmd: list[str] = deepcopy(self.qmd_to_ipynb)
            cmd.append(str(self.path))
            result = subprocess.run(cmd)
            if not result:
                print("Conversation successful!")
            else:
                print(f"Could not convert '{self.path}'")

        elif self.file["extension"] == ".Rmd":
            cmd: list[str] = deepcopy(self.rmd_to_ipynb)
            cmd.append(str(self.path))
            result = subprocess.run(cmd)
            if not result:
                print("Conversation successful!")
            else:
                print(f"Could not convert '{self.path}'")

        else:
            print("File is already a '.ipynb' file. No need for conversion.")

    def remove_temp(self) -> None:
        os.remove("./temp")

    def chunk(self):
        file_copy: dict = deepcopy(self.file)
        notebook_path: str = str(Path("./temp", self.file["name"] + ".ipynb"))

        self.convert()
        with open(notebook_path, "r") as f:
            notebook: dict = json.load(f)

            content: list[dict] = [
                {cell["cell_type"]: cell["source"]}
                for cell in notebook["cells"]
                if cell["cell_type"] in ["code", "markdown"]
            ]

        file_copy["content"] = content
        return file_copy
