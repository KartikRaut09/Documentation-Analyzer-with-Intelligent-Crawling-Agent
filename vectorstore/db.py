from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

def build_vectorstore(chunks):
    if not chunks:
        raise ValueError("No chunks available to index. Crawl a valid site first.")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    texts = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory="chroma_db"
    )

    # newer versions of langchain-chroma automatically persist when a
    # `persist_directory` is provided.  The old `.persist()` method has been
    # removed from the public API, which was causing an AttributeError.  If
    # explicit persistence is ever needed, the underlying client object has a
    # `persist` method:
    #
    #     if hasattr(vectorstore, "_client"):
    #         vectorstore._client.persist()
    #
    # For now simply return the store and let it manage persistence itself.
    return vectorstore
