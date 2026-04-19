import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from pathlib import Path
from rank_bm25 import BM25Okapi

import faiss
import numpy as np
import google.generativeai as genai

from app.utils import backend_root, load_json, normalize_text, require_env


class Retriever:

    def __init__(self):
        self.data_file = backend_root() / "data" / "erp_chunks.json"
        self.data = load_json(self.data_file)
        self.texts = [normalize_text(d["text"]) for d in self.data]
        self.tokenized_texts = [text.split() for text in self.texts]
        self.bm25 = BM25Okapi(self.tokenized_texts)
        self._configure_model()
        self.index = self._build_index()
    
    def keyword_search(self, query, k=5):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        top_indices = np.argsort(scores)[::-1][:k]
        return top_indices

    def _configure_model(self):
        try:
            api_key = require_env("GEMINI_API_KEY")
            if api_key.startswith("AIzaSyAXlKzgn"):  # Placeholder key
                raise ValueError("Placeholder API key detected")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-flash-latest", generation_config={"temperature": 0.3})
            self.api_available = True
        except Exception as e:
            print(f"Warning: Gemini API not available ({e}). Using mock responses.")
            self.api_available = False
            self.model = None

    def embed(self, text):
        if not self.api_available:
            return np.random.rand(768).astype("float32")

        try:
            response = genai.embed_content(
                model="text-embedding-004",
                content=normalize_text(text)
            )
            return np.array(response["embedding"], dtype="float32")
        except Exception as e:
            print(f"Embedding error: {e}")
            return np.random.rand(768).astype("float32")

    def _build_index(self):
        cache_path = self.data_file.parent / "erp_chunks_embeddings.npy"

        if cache_path.exists():
            embeddings = np.load(cache_path)
            faiss.normalize_L2(embeddings)
        else:
            embeddings = np.vstack([self.embed(text) for text in self.texts])
            faiss.normalize_L2(embeddings)
            np.save(cache_path, embeddings)

        if embeddings.size == 0:
            raise RuntimeError("No embeddings were generated")

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        return index
    
    def rewrite_query(self, question):
        return f"ERP process: {question}"

    def retrieve(self, query):
        try:
            query = self.rewrite_query(query)
            logger.info(f"Retrieving for query: {query}")

            q_vec = self.embed(query).reshape(1, -1)
            faiss.normalize_L2(q_vec)

            distances, vector_idx = self.index.search(q_vec, k=8)
            logger.info(f"Top distances: {distances[0]}")

            keyword_idx = self.keyword_search(query, k=5)

            combined_indices = list(set(vector_idx[0]) | set(keyword_idx))

            context, sources = [], []

            for i in combined_indices:
                context.append(self.texts[i])
                sources.append(self.data[i]["source"])

            logger.info(f"Combined results count: {len(context)}")

            query_words = set(query.lower().split())

            scored = []
            for ctx, src in zip(context, sources):
                overlap = len(query_words & set(ctx.lower().split()))
                scored.append((overlap, ctx, src))

            scored.sort(reverse=True)
            top_results = scored[:5]

            final_context = [item[1] for item in top_results]
            final_sources = [item[2] for item in top_results]

            if not final_context:
                return "No relevant ERP context found.", []

            context_text = "\n\n---\n\n".join(final_context)[:2000]

            return context_text, final_sources

        except Exception as e:
            logger.exception("Retrieve failed")
            return "", []        
    
    def generate(self, prompt):
        if not self.api_available:
            return "Mock response: This is a demo answer. Please configure a valid GEMINI_API_KEY for real responses."
        response = self.model.generate_content(prompt)
        return response.text.strip()
