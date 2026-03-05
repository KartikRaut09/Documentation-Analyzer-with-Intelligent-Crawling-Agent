from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    """Split crawled documents into smaller text chunks.

    Chunks are deduplicated across all documents and empty
    strings are ignored so that the vector store doesn't receive
    repeated or meaningless entries.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = []
    seen_texts = set()

    for doc in documents:
        split_texts = splitter.split_text(doc["content"])

        for chunk in split_texts:
            text = chunk.strip()
            if not text or text in seen_texts:
                # skip empty or already-added chunk
                continue

            seen_texts.add(text)
            chunks.append({
                "text": text,
                "source": doc["url"]
            })

    return chunks