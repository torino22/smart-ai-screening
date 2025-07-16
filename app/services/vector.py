import re
import uuid
from datetime import datetime, timezone
from typing import List

import chromadb
import nltk
from chromadb.config import Settings
from nltk.data import find
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer

from app.config.settings import (
    EMBEDDING_MODEL,
    VECTOR_DIR,
    MIN_WORDS,
    MAX_WORDS,
    TOP_N_RESULTS
)
from app.pydantics.schemas import GenericServiceResponse

current_embedding_model = SentenceTransformer(EMBEDDING_MODEL) # Initializing once since it takes more time


class EmbeddingFunction:
    def __init__(self, model):
        self.model = model

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input, convert_to_tensor=False).tolist()

    def name(self) -> str:
        return "sentence-transformers"

embedding_fn = EmbeddingFunction(current_embedding_model)


class VectorService:
    def __init__(self):
        self.collection = self._init_chromadb()
        self._ensure_nltk_data()

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is available"""
        try:
            find("tokenizers/punkt")
            find("tokenizers/punkt/english.pickle")
            find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt")
            nltk.download("punkt_tab")


    def _init_chromadb(self):
        """Initializing persisted chromaDB"""
        self.chroma_client = chromadb.PersistentClient(
            path=VECTOR_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        return self.chroma_client.get_or_create_collection(
            name="interview_faqs",
            embedding_function=embedding_fn
        )

    @staticmethod
    def embedding_function(texts: List[str]) -> List[List[float]]:
        return current_embedding_model.encode(texts, convert_to_tensor=False).tolist()


    def clean_text(self, text: str) -> str:
        """Clean invisible and redundant characters."""
        text = text.replace("\u200b", "")
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\t+", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text


    def chunk_text(self, transcript: str) -> GenericServiceResponse:
        """Split text into word-based chunks."""
        try:
            cleaned_transcript = self.clean_text(transcript)
            sentences = sent_tokenize(cleaned_transcript)
            chunks, current_chunk, word_count = [], [], 0

            for sentence in sentences:
                words = sentence.split()
                if word_count + len(words) > MAX_WORDS:
                    if word_count >= MIN_WORDS:
                        chunks.append(" ".join(current_chunk))
                        current_chunk, word_count = [sentence], len(words)
                    else:
                        current_chunk.append(sentence)
                        word_count += len(words)
                else:
                    current_chunk.append(sentence)
                    word_count += len(words)

            if current_chunk:
                chunks.append(" ".join(current_chunk))
            return GenericServiceResponse(
                   result=chunks
                   )

        except Exception as e:
            return GenericServiceResponse(
                success=False,
                error=f"Search failed: {str(e)}"
            )


    def embed_and_store(self,
                        session_id: str,
                        rewritten_chunks: list,
                        ) -> GenericServiceResponse:
        """
        Clean, chunk, embed, and store into ChromaDB.

        Args:
            text: Large transcript or FAQ text
            source: Tag to identify where this data came from

        Returns:
            Chunk and vector store stats
        """
        try:

            for i, chunk in enumerate(rewritten_chunks, 1):
                try:
                    chunk_id = f"{uuid.uuid4()}"
                    metadata = {
                        "session_id": session_id,
                        "chunk_num": i,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }

                    self.collection.add(
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[chunk_id]
                    )
                except Exception as e:
                    print(f"Error occurred for this chunk: {chunk}, error: {str(e)}")
                    continue

            return GenericServiceResponse(
                   message=f"Totally {len(rewritten_chunks)} chunks stored for this session id: {session_id}."
                   )
        except Exception as e:
            return GenericServiceResponse(
                   success=False,
                   error=f"Error {str(e)}"
                   )

    def semantic_search(self,
                        session_id: str,
                        query: str,
                        top_k: int = TOP_N_RESULTS
                        ) -> GenericServiceResponse:
        """
        Perform semantic search within the vector store for a specific session ID.

        Args:
            session_id (str): Session identifier to filter stored chunks.
            query (str): User query to semantically search.
            top_k (int): Number of top matching chunks to return.

        Returns:
            GenericServiceResponse: Contains matching chunks and metadata.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"session_id": session_id}
            )

            matched_chunks = [
                {
                    "chunk": doc,
                    "score": score,
                    "metadata": meta
                }
                for doc, score, meta in zip(
                    results.get("documents", [[]])[0],
                    results.get("distances", [[]])[0],
                    results.get("metadatas", [[]])[0]
                )
            ]

            result =  [item["chunk"] for item in matched_chunks]
            # print(result)

            return GenericServiceResponse(
                result=result,
                message=f"{len(matched_chunks)} chunks found for session: {session_id}"
            )

        except Exception as e:
            return GenericServiceResponse(
                success=False,
                error=f"Search failed: {str(e)}"
            )

