"""CV upload and processing — plain functions grouped by concern.

All CPU-bound functions are synchronous and must be called via
asyncio.to_thread() from async contexts to avoid blocking the event loop.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastembed import SparseTextEmbedding, TextEmbedding
from fastapi import UploadFile
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from core.config import settings


async def save_upload(file: UploadFile, candidate_id: uuid.UUID) -> str:
    """Save *file* under uploads/cvs/<candidate_id>/<new-uuid>.pdf.

    Returns the path relative to settings.cv_upload_dir so it can be
    stored in the DB and later reconstructed into a URL or disk path.
    """
    rel_dir = f"cvs/{candidate_id}"
    abs_dir = Path(settings.cv_upload_dir) / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    rel_path = f"{rel_dir}/{uuid.uuid4()}.pdf"
    abs_path = Path(settings.cv_upload_dir) / rel_path

    content = await file.read()
    abs_path.write_bytes(content)

    return rel_path


def extract_text(file_path: str) -> str:
    """Return concatenated text from all pages of the PDF.

    *file_path* is relative to settings.cv_upload_dir.
    """
    abs_path = Path(settings.cv_upload_dir) / file_path
    reader = PdfReader(str(abs_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str) -> list[str]:
    """Split *text* into indexable chunks via a two-stage pipeline.

    Stage 1 — SemanticChunker groups sentences by embedding similarity,
    producing topic-aligned chunks regardless of raw size.

    Stage 2 — RecursiveCharacterTextSplitter enforces chunk_size /
    chunk_overlap limits so no chunk exceeds the embedding model's
    context window.
    """
    embeddings = FastEmbedEmbeddings(model_name=settings.dense_embedding_model)

    semantic_docs = SemanticChunker(
        embeddings, breakpoint_threshold_type="percentile"
    ).create_documents([text])

    final_docs = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    ).split_documents(semantic_docs)

    return [doc.page_content for doc in final_docs if doc.page_content.strip()]


def _ensure_cv_collection(client: QdrantClient) -> None:
    """Create the cv_chunks collection if it does not exist yet."""
    existing = {c.name for c in client.get_collections().collections}
    if settings.qdrant_cv_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_cv_collection,
            vectors_config={
                "dense": VectorParams(
                    size=settings.dense_vector_size,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )


def index_cv_chunks(
    document_id: uuid.UUID,
    candidate_id: uuid.UUID,
    chunks: list[str],
    client: QdrantClient,
) -> None:
    """Embed *chunks* and upsert into the cv_chunks Qdrant collection.

    Payload design:
      candidate_id — primary Qdrant filter: HR queries always filter by
                     candidate first, then run hybrid search within that
                     candidate's chunks only.
      document_id  — traces a chunk back to its CVDocument row in PG.
      chunk_index  — preserves reading order within the document.
    """
    _ensure_cv_collection(client)

    dense_vecs = list(
        TextEmbedding(model_name=settings.dense_embedding_model).embed(chunks)
    )
    sparse_vecs = list(
        SparseTextEmbedding(model_name=settings.sparse_embedding_model).embed(chunks)
    )

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "dense": dense_vec.tolist(),
                "sparse": SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist(),
                ),
            },
            payload={
                "candidate_id": str(candidate_id),
                "document_id": str(document_id),
                "chunk_index": idx,
            },
        )
        for idx, (dense_vec, sparse_vec) in enumerate(zip(dense_vecs, sparse_vecs))
    ]

    client.upsert(collection_name=settings.qdrant_cv_collection, points=points)
