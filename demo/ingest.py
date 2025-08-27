from dotenv import load_dotenv
load_dotenv()

import os
from .extractor.pdf.pdf_extractor import PDFExtractor
from .chunker.chunker import Chunker
from .model_provider import generate_embeddings
from .vector_store import delete_collection, get_collection

DOCS_DIR = os.environ.get("DOCS_DIR", "./data/docs")

def ingest():
    # Clear existing collection
    delete_collection()

    extractor = PDFExtractor()
    chunker = Chunker()
    doc_id = 0
    for filename in os.listdir(DOCS_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(DOCS_DIR, filename)
            text = extractor.extract(pdf_path)
            chunks = chunker.chunk(text)
            if not chunks:
                continue
            embeddings = generate_embeddings(chunks)
            # Add each chunk as a separate document
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                get_collection().add(
                    documents=[chunk],
                    ids=[f"{filename}_{i}"],
                    embeddings=embedding
                )
                doc_id += 1
    print(f"Added {doc_id} chunks to ChromaDB from PDFs in {DOCS_DIR}")
