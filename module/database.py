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
        embeddings_list: list[list[float]],,
        metadatas_list: list[dict],
    ) -> None:
        """The main method of the writer object writing the provided information in the database as a side-effect.

        Args:
            ids_list (list[str]): A list of unique ids, one per file.
            documents_list (list[str]): A list of documents to embed and then stores.
            embeddings_list (list[list[float]]): A list of embedded vectors for each documents
            metadatas_list (list[dict]): A list of dictionaries, containing metadata information about the documents

        Returns: None"""
        self.collection.add(
            ids=ids_list,
            documents=documents_list,
            embeddings=embeddings_list,
            metadatas=metadatas_list,
        )
