import logging
import hashlib
from pathlib import Path

import faiss
import numpy as np
from google import genai
from google.genai import types
from google.api_core import exceptions
from rank_bm25 import BM25Okapi
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# Existing project imports
from app.logger import logger
from app.utils import (
    backend_root,
    load_json,
    normalize_text,
    require_env
)


class Retriever:

    def __init__(self):

        # =========================
        # DATA LOADING
        # =========================
        self.data_file = (
            backend_root()
            / "data"
            / "erp_chunks.json"
        )

        self.data = load_json(self.data_file)

        if not self.data:
            raise RuntimeError(
                "erp_chunks.json is empty"
            )

        # =========================
        # TEXT PREPROCESSING
        # =========================
        self.texts = [
            normalize_text(d["text"])
            for d in self.data
        ]

        self.tokenized_texts = [
            text.split()
            for text in self.texts
        ]

        # =========================
        # BM25 INITIALIZATION
        # =========================
        self.bm25 = BM25Okapi(
            self.tokenized_texts
        )

        # =========================
        # GEMMA MODEL CONFIG
        # =========================
        self._configure_model()

        # =========================
        # BUILD VECTOR INDEX
        # =========================
        self.index = self._build_index()

    # ======================================================
    # GEMMA CONFIGURATION
    # ======================================================

    def _configure_model(self):

        try:

            api_key = require_env(
                "GEMINI_API_KEY"
            )

            logger.info(
                f"API KEY LOADED: {bool(api_key)}"
            )

            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY is missing"
                )

            # Initialize Google GenAI client
            self.client = genai.Client(
                api_key=api_key
            )

            # Recommended stable Gemma model
            self.model_name = "gemma-3-27b-it"

            # Generation config
            self.generation_config = (
                types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.95,
                    max_output_tokens=1024
                )
            )

            self.api_available = True

            logger.info(
                "Gemma model initialized successfully"
            )

        except Exception as e:

            logger.exception(
                f"Gemma initialization failed: {e}"
            )

            self.api_available = False
            self.client = None

    # ======================================================
    # FALLBACK EMBEDDING
    # ======================================================

    def _fallback_embedding(self, text):

        hash_digest = hashlib.sha256(
            text.encode()
        ).digest()

        embedding = np.array(
            [b for b in hash_digest],
            dtype=np.float32
        )

        embedding = np.pad(
            embedding,
            (0, 384 - len(embedding)),
            mode="constant"
        )

        return embedding[:384]

    # ======================================================
    # EMBEDDING FUNCTION
    # ======================================================

    @retry(
        retry=retry_if_exception_type(
            exceptions.ResourceExhausted
        ),
        wait=wait_exponential(
            multiplier=1,
            min=4,
            max=60
        ),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def embed(self, text):

        if not self.api_available:

            logger.warning(
                "Using fallback embeddings"
            )

            return self._fallback_embedding(text)

        try:

            response = (
                self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=normalize_text(text)
                )
            )

            embedding = np.array(
                response.embeddings[0].values,
                dtype=np.float32
            )

            return embedding

        except Exception as e:

            logger.warning(
                f"Embedding failed: {e}"
            )

            return self._fallback_embedding(text)

    # ======================================================
    # BUILD FAISS INDEX
    # ======================================================

    def _build_index(self):

        cache_path = (
            self.data_file.parent
            / "erp_chunks_embeddings.npy"
        )

        logger.info(
            "Building FAISS index..."
        )

        logger.info(
            f"Total documents: {len(self.texts)}"
        )

        # =========================
        # LOAD CACHED EMBEDDINGS
        # =========================
        if cache_path.exists():

            logger.info(
                "Loading cached embeddings..."
            )

            embeddings = np.load(cache_path)

            faiss.normalize_L2(
                embeddings
            )

        # =========================
        # GENERATE EMBEDDINGS
        # =========================
        else:

            logger.info(
                "Generating embeddings..."
            )

            embeddings = np.vstack([
                self.embed(text)
                for text in self.texts
            ])

            faiss.normalize_L2(
                embeddings
            )

            np.save(
                cache_path,
                embeddings
            )

            logger.info(
                f"Embeddings cached at: {cache_path}"
            )

        if embeddings.size == 0:
            raise RuntimeError(
                "No embeddings generated"
            )

        dim = embeddings.shape[1]

        logger.info(
            f"Embedding dimension: {dim}"
        )

        # Inner Product similarity
        index = faiss.IndexFlatIP(dim)

        index.add(embeddings)

        logger.info(
            "FAISS index created successfully"
        )

        return index

    # ======================================================
    # QUERY REWRITING
    # ======================================================

    def rewrite_query(self, question):

        return f"""
        ERP enterprise process question:
        {question}
        """.strip()

    # ======================================================
    # BM25 KEYWORD SEARCH
    # ======================================================

    def keyword_search(self, query, k=5):

        tokenized_query = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        top_indices = np.argsort(
            scores
        )[::-1][:k]

        return top_indices

    # ======================================================
    # HYBRID RETRIEVAL
    # ======================================================

    def retrieve(self, query):

        # =========================
        # QUERY REWRITE
        # =========================
        query = self.rewrite_query(query)

        # =========================
        # VECTOR SEARCH
        # =========================
        q_vec = self.embed(query).reshape(1, -1)

        faiss.normalize_L2(q_vec)

        distances, vector_idx = (
            self.index.search(q_vec, k=8)
        )

        # =========================
        # BM25 SEARCH
        # =========================
        keyword_idx = self.keyword_search(
            query,
            k=5
        )

        # =========================
        # HYBRID MERGE
        # =========================
        combined_indices = list(
            set(vector_idx[0])
            | set(keyword_idx)
        )

        context = []
        sources = []

        for i in combined_indices:

            if i >= len(self.data):
                continue

            context.append(
                self.texts[i]
            )

            sources.append(
                self.data[i].get(
                    "source",
                    "Unknown Source"
                )
            )

        # =========================
        # SIMPLE RERANKING
        # =========================
        query_words = set(
            query.lower().split()
        )

        scored = []

        for ctx, src in zip(
            context,
            sources
        ):

            overlap = len(
                query_words
                & set(ctx.lower().split())
            )

            scored.append(
                (overlap, ctx, src)
            )

        scored.sort(
            reverse=True
        )

        top_results = scored[:5]

        final_context = [
            item[1]
            for item in top_results
        ]

        final_sources = [
            item[2]
            for item in top_results
        ]

        context_text = "\n\n---\n\n".join(
            final_context
        )

        # Context window protection
        context_text = context_text[:4000]

        return context_text, final_sources

    # ======================================================
    # GEMMA GENERATION
    # ======================================================

    @retry(
        retry=retry_if_exception_type(
            exceptions.ResourceExhausted
        ),
        wait=wait_exponential(
            multiplier=1,
            min=4,
            max=60
        ),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def generate(self, prompt):

        if not self.api_available:

            return (
                "Mock response: "
                "Please configure GEMINI_API_KEY"
            )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self.generation_config
                )
            )

            if response.text:

                return response.text.strip()

            return "Model returned no content."

        except Exception as e:

            logger.exception(
                f"Generation failed: {e}"
            )

            return (
                f"Generation Error: {str(e)}"
            )