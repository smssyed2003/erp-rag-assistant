from pathlib import Path

import faiss
import numpy as np
import google.generativeai as genai

from app.utils import backend_root, load_json, normalize_text, require_env


class Retriever:

    def __init__(self):
        self.data_file = backend_root() / "data" / "erp_chunks.json"
        self.data = load_json(self.data_file)
        self.texts = [normalize_text(d["text"]) for d in self.data]
        self._configure_model()
        self.index = self._build_index()

    def _configure_model(self):
        try:
            api_key = require_env("GEMINI_API_KEY")
            if api_key.startswith("AIzaSyAXlKzgn"):  # Placeholder key
                raise ValueError("Placeholder API key detected")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.api_available = True
        except Exception as e:
            print(f"Warning: Gemini API not available ({e}). Using mock responses.")
            self.api_available = False
            self.model = None

    def embed(self, text):
        if not self.api_available:
            # Return random embedding for demo
            import numpy as np
            return np.random.rand(768).astype("float32")
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=normalize_text(text)
        )
        return np.array(response["embedding"], dtype="float32")

    def _build_index(self):
        cache_path = self.data_file.parent / "erp_chunks_embeddings.npy"

        if cache_path.exists():
            embeddings = np.load(cache_path)
        else:
            embeddings = np.vstack([self.embed(text) for text in self.texts])
            np.save(cache_path, embeddings)

        if embeddings.size == 0:
            raise RuntimeError("No embeddings were generated for the ERP knowledge base.")

        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index

    def retrieve(self, query):
        q_vec = self.embed(query)
        _, idx = self.index.search(np.array([q_vec], dtype="float32"), k=3)

        context = []
        sources = []
        for i in idx[0]:
            context.append(self.texts[i])
            sources.append(self.data[i]["source"])

        return "\n\n".join(context), sources

    def generate(self, prompt):
        if not self.api_available:
            return "Mock response: This is a demo answer. Please configure a valid GEMINI_API_KEY for real responses."
        response = self.model.generate_content(prompt)
        return response.text.strip()
