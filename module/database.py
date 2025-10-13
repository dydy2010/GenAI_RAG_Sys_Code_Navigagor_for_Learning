import chromadb
from dataclasses import dataclass, field


@dataclass
class Database:
    """A dataclass meant to hold the client to the Chroma Database.
    As the client enables communication with the database, efficiency requires creating it once and then reusing it.

    Args:
        client_path (str): the path leading to the chroma database files.
        Defaults to './chroma-db/', which is the default path of the database inside the repository.

        client (chromadb.PersistentClient): the client object from the `chromadb` library enabling communication with the database."""

    client_path: str = "./chroma-db/"
    client: chromadb.PersistentClient = field(init=False)

    def __post_init__(self):
        self.client = chromadb.PersistentClient(self.client_path)


class DatabaseWriter:
    """A class instantiating a writer object enabling writing into a specific collection of the database."""

    def __init__(
        self,
        database: Database,
        collection_name: str,
    ):
        """Instantiate a writer object, enabling to write information into the designated collection of the designated client.

        Args:
            database (Database): a `Database` dataclass.
            collection_name (str): The collection name you wish to write information in."""

        self.client = database.client
        self.collection = self.client(name=collection_name)
        return self

    def write(
        self,
        ids_list: list[str],
        documents_list: list[str],
        metadatas_list: list[dict],
    ) -> None:
        """The main method of the writer object writing the provided information in the database as a side-effect.

        Args:
            ids_list (list[str]): A list of unique ids, one per file.
            documents_list (list[str]): A list of documents to embed and then stores.
            metadatas_list (list[dict]): A list of dictionaries, containing metadata information about the documents

        Returns: None"""
        self.collection.add(
            ids=ids_list, documents=documents_list, metadatas=metadatas_list
        )


# Add a collection (similar to a table) to the database.
# 'embedding_function' defines the embedding model
# INFO: Only need to be created once.
database = Database()
code_collection = database.client.create_collection(
    name="code",
    embedding_function=CodeEmbedder,
    metadata={
        "description": "A collection storing code files, e.g. '.py' or '.R' files."
    },
)

notebook_collection = database.client.create_collection(
    name="notebook",
    metadata={
        "description": "A collection storing mixes of code and textes, e.g. Jupyter Notebook, Quarto document."
    },
)
