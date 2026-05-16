"""
Embedding Service for generating and managing code embeddings
"""
import json
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database import CodeEmbedding, Project
from app.services.watsonx_client import watsonx_client


class EmbeddingService:
    """Service for generating and managing code embeddings"""

    def __init__(self):
        self.chunk_size = 500   # characters per chunk
        self.overlap = 50       # overlap between chunks

    def _chunk_code(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Split code into overlapping line-based chunks."""
        chunks = []
        lines = code.split('\n')
        current_chunk: List[str] = []
        current_size = 0
        chunk_index = 0

        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline

            if current_size + line_size > self.chunk_size and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'file_path': file_path,
                    'start_line': i - len(current_chunk) + 1,
                    'end_line': i,
                    'chunk_index': chunk_index,
                })

                overlap_lines = current_chunk[-3:] if len(current_chunk) > 3 else current_chunk
                current_chunk = overlap_lines + [line]
                current_size = sum(len(l) + 1 for l in current_chunk)
                chunk_index += 1
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'file_path': file_path,
                'start_line': len(lines) - len(current_chunk) + 1,
                'end_line': len(lines),
                'chunk_index': chunk_index,
            })

        return chunks

    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate real semantic embeddings via IBM granite-embedding model.
        Falls back to zero vectors if the API call fails.
        """
        try:
            return watsonx_client.embed(texts)
        except Exception as e:
            print(f"Error generating embeddings from IBM API: {e}")
            # Fallback: zero vectors (will yield zero similarity scores)
            return [[0.0] * 768 for _ in texts]

    def generate_embeddings_for_project(
        self,
        db: Session,
        project_id: int,
        code_files: Dict[str, str],
    ) -> int:
        """
        Generate semantic embeddings for all code files in a project.
        Chunks are embedded in batches for efficiency.

        Returns the number of embedding records created.
        """
        if not code_files:
            raise ValueError("code_files is empty — refusing to wipe existing embeddings")

        # Collect all chunks first so we can batch-embed
        all_chunks: List[Dict[str, Any]] = []
        for file_path, code in code_files.items():
            if not code.strip():
                continue
            all_chunks.extend(self._chunk_code(code, file_path))

        if not all_chunks:
            return 0

        # Batch embed — IBM API handles up to 1000 inputs at once
        BATCH = 100
        all_vectors: List[List[float]] = []
        for i in range(0, len(all_chunks), BATCH):
            batch_texts = [c['text'] for c in all_chunks[i:i + BATCH]]
            vectors = self._generate_embeddings_batch(batch_texts)
            all_vectors.extend(vectors)

        # Clear existing embeddings only now that we have replacement data
        db.query(CodeEmbedding).filter(
            CodeEmbedding.project_id == project_id
        ).delete()

        for chunk, vector in zip(all_chunks, all_vectors):
            embedding = CodeEmbedding(
                project_id=project_id,
                file_path=chunk['file_path'],
                code_chunk=chunk['text'],
                embedding=json.dumps(vector),
                chunk_index=chunk['chunk_index'],
            )
            db.add(embedding)

        db.commit()
        return len(all_chunks)

    def search_similar_code(
        self,
        db: Session,
        project_id: int,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Embed the query and return the top-k most similar code chunks via
        cosine similarity against stored embeddings.
        """
        # Embed the query using the same IBM model
        try:
            query_vectors = watsonx_client.embed([query])
            query_embedding = np.array(query_vectors[0])
        except Exception as e:
            print(f"Error embedding query: {e}")
            return []

        embeddings = db.query(CodeEmbedding).filter(
            CodeEmbedding.project_id == project_id
        ).all()

        if not embeddings:
            return []

        results = []
        for emb in embeddings:
            try:
                emb_vector = np.array(json.loads(emb.embedding))
                # Cosine similarity (vectors are unit-normalised by the IBM model)
                similarity = float(np.dot(query_embedding, emb_vector))
                results.append({
                    'file_path': emb.file_path,
                    'code_chunk': emb.code_chunk,
                    'similarity': similarity,
                    'chunk_index': emb.chunk_index,
                })
            except Exception as e:
                print(f"Error calculating similarity: {e}")
                continue

        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = [r for r in results if r['similarity'] >= min_similarity]
        return results[:top_k]


# Global service instance
embedding_service = EmbeddingService()

# Made with Bob
