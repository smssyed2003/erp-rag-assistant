import os
import json
import hashlib
import logging
import faiss
import numpy as np
import google.generativeai as genai
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from datetime import datetime
from dotenv import load_dotenv
import gdown

# Load variables from .env file
load_dotenv()

# Setup Logging for Corporate Standards
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CorporateRAG:
    def __init__(self, data_folder="data", db_path="vector_db/erp_index.faiss"):
        self.data_folder = data_folder
        self.db_path = db_path
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = []
        self.metadata = []
        
        # Configure Gemini using .env variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY not found. Check your .env file!")
        
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel("gemini-flash-latest")

        # Download PDFs from Google Drive if not present
        self._download_pdfs()

        # Load or Create Index
        self.state = self._load_state()
        self.current_file_checksums = self._compute_file_checksums()
        self._ingest_docs(file_order=self._determine_file_order())

        if os.path.exists(self.db_path) and self.state:
            logging.info("Loading existing Vector Database from disk...")
            self.index = faiss.read_index(self.db_path)
            if self._should_rebuild_index():
                logging.info("Detected changed or removed documents. Rebuilding full index...")
                self._build_index()
            elif self._has_new_files():
                self._append_new_chunks()
            elif self.index.ntotal != len(self.chunks):
                logging.info("Existing index chunk count differs from current documents. Rebuilding index...")
                self._build_index()
            else:
                logging.info("Existing vector index is up-to-date.")
        else:
            logging.info("No database found. Building new vector index from all PDFs...")
            self._build_index()

    def _download_pdfs(self):
        """Download PDFs from Google Drive folder if data folder is empty."""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        # Check if PDFs are already downloaded
        pdf_files = [f for f in os.listdir(self.data_folder) if f.endswith('.pdf')]
        if pdf_files:
            logging.info(f"Found {len(pdf_files)} PDF files in {self.data_folder}. Skipping download.")
            return
        
        # Google Drive folder URL - replace with your actual folder ID
        folder_url = "https://drive.google.com/drive/folders/18inq6xaouUQGaVe-MZgbnQuwiETk6mK4?usp=sharing"
        
        # Extract folder ID from URL
        if "folders/" in folder_url:
            folder_id = folder_url.split("folders/")[1].split("?")[0]
        else:
            logging.error("Invalid Google Drive folder URL")
            return
        
        logging.info(f"Downloading PDFs from Google Drive folder: {folder_id}")
        try:
            gdown.download_folder(id=folder_id, output=self.data_folder, quiet=False)
            logging.info("PDFs downloaded successfully.")
        except Exception as e:
            logging.error(f"Failed to download PDFs: {e}")
            raise

    def _ingest_docs(self, file_order=None):

        if os.path.exists(self.db_path) and self.state:
            logging.info("Loading existing Vector Database from disk...")
            self.index = faiss.read_index(self.db_path)
            if self._should_rebuild_index():
                logging.info("Detected changed or removed documents. Rebuilding full index...")
                self._build_index()
            elif self._has_new_files():
                self._append_new_chunks()
            elif self.index.ntotal != len(self.chunks):
                logging.info("Existing index chunk count differs from current documents. Rebuilding index...")
                self._build_index()
            else:
                logging.info("Existing vector index is up-to-date.")
        else:
            logging.info("No database found. Building new vector index from all PDFs...")
            self._build_index()

    def _ingest_docs(self, file_order=None):
        """Standardizes multi-PDF ingestion and recursive-style chunking."""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            return

        if file_order is None:
            file_order = sorted(self.current_file_checksums.keys())

        self.file_order = file_order
        self.chunks = []
        self.metadata = []

        for file in file_order:
            path = os.path.join(self.data_folder, file)
            reader = PdfReader(path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Overlapping chunks to keep context
                    page_chunks = [text[i:i+800] for i in range(0, len(text), 600)]
                    for chunk in page_chunks:
                        self.chunks.append(chunk)
                        self.metadata.append({"source": file, "page": i+1})
        logging.info(f"Successfully loaded {len(self.chunks)} text chunks.")

    def _state_path(self):
        return os.path.join(os.path.dirname(self.db_path), "state.json")

    def _load_state(self):
        try:
            with open(self._state_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logging.warning("Could not load saved state: %s", e)
            return {}

    def _save_state(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        state = {
            "file_order": self.file_order,
            "file_checksums": self.current_file_checksums,
            "chunk_count": len(self.chunks),
        }
        with open(self._state_path(), "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def _file_checksum(self, path):
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _compute_file_checksums(self):
        checksums = {}
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            return checksums

        for file in sorted(os.listdir(self.data_folder)):
            if file.endswith(".pdf"):
                path = os.path.join(self.data_folder, file)
                checksums[file] = self._file_checksum(path)

        return checksums

    def _determine_file_order(self):
        current_files = list(self.current_file_checksums.keys())
        if not self.state:
            return current_files

        old_order = self.state.get("file_order", [])
        old_checksums = self.state.get("file_checksums", {})
        current_set = set(current_files)

        changed_files = [
            f
            for f in current_files
            if f in old_checksums and self.current_file_checksums[f] != old_checksums[f]
        ]
        removed_files = [f for f in old_order if f not in current_set]

        if changed_files or removed_files:
            return current_files

        unchanged_files = [f for f in old_order if f in current_set]
        new_files = [f for f in current_files if f not in old_order]
        return unchanged_files + sorted(new_files)

    def _should_rebuild_index(self):
        if not self.state:
            return True

        old_checksums = self.state.get("file_checksums", {})
        old_order = self.state.get("file_order", [])
        current_set = set(self.current_file_checksums.keys())

        changed_files = [
            f
            for f in self.current_file_checksums
            if f in old_checksums and self.current_file_checksums[f] != old_checksums[f]
        ]
        removed_files = [f for f in old_order if f not in current_set]
        return bool(changed_files or removed_files)

    def _has_new_files(self):
        if not self.state:
            return False
        old_files = set(self.state.get("file_order", []))
        return any(f for f in self.current_file_checksums if f not in old_files)

    def _append_new_chunks(self):
        old_chunk_count = self.state.get("chunk_count", 0)
        new_chunks = self.chunks[old_chunk_count:]
        if not new_chunks:
            logging.info("No new document chunks to append to the existing index.")
            return

        logging.info("Embedding and appending %d new chunks to the existing vector index...", len(new_chunks))
        embeddings = self.embed_model.encode(new_chunks, show_progress_bar=True)
        self.index.add(np.array(embeddings).astype("float32"))
        faiss.write_index(self.index, self.db_path)
        self._save_state()
        logging.info("Successfully updated the vector index with new documents.")

    def rebuild_index(self, force=False):
        """Refresh the vector index manually and optionally force a full rebuild."""
        self.state = self._load_state()
        self.current_file_checksums = self._compute_file_checksums()
        self._ingest_docs(file_order=self._determine_file_order())

        if force:
            logging.info("Force rebuild requested. Rebuilding full index...")
            self._build_index()
            return {"status": "rebuilt", "reason": "force", "chunk_count": len(self.chunks)}

        if self._should_rebuild_index():
            logging.info("Detected changed or removed documents. Rebuilding full index...")
            self._build_index()
            return {"status": "rebuilt", "reason": "changed_or_removed", "chunk_count": len(self.chunks)}

        if self._has_new_files():
            self._append_new_chunks()
            return {"status": "appended", "reason": "new_files", "chunk_count": len(self.chunks)}

        if os.path.exists(self.db_path) and getattr(self, "index", None) is not None and self.index.ntotal == len(self.chunks):
            logging.info("Index already up-to-date. No action taken.")
            return {"status": "up_to_date", "reason": "no_changes", "chunk_count": len(self.chunks)}

        logging.info("Index state mismatch detected. Rebuilding full index...")
        self._build_index()
        return {"status": "rebuilt", "reason": "chunk_mismatch", "chunk_count": len(self.chunks)}

    def _build_index(self):
        """Creates and saves the FAISS index to avoid re-training."""
        logging.info("Generating embeddings for documents... this may take a moment.")
        embeddings = self.embed_model.encode(self.chunks, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        faiss.write_index(self.index, self.db_path)
        self._save_state()
        logging.info("Vector Database saved successfully to 'vector_db/' folder.")

    def query(self, user_question):
        """Production retrieval logic with strict source citation."""
        query_vec = self.embed_model.encode([user_question])
        distances, indices = self.index.search(np.array(query_vec).astype('float32'), k=3)

        context_blocks = []
        sources = set()
        for i in indices[0]:
            if i != -1:
                context_blocks.append(self.chunks[i])
                sources.add(self.metadata[i]['source'])

        context_text = "\n\n----- CONTENT BLOCK -----\n\n".join(context_blocks)
        
        prompt = f"""
        SYSTEM ROLE: You are an expert ERP Functional Consultant for Finance, P2P, and O2C.
        INSTRUCTION: Answer the question using ONLY the context provided below. 
        If the answer isn't in the context, say: "I'm sorry, the current documentation doesn't cover that process."

        CONTEXT:
        {context_text}
        
        QUESTION: {user_question}
        
        ANSWER FORMAT: Provide a clear, step-by-step guidance answer. 
        At the end, list the sources: {list(sources)}
        """
        
        response = self.llm.generate_content(prompt)
        return {"answer": response.text, "sources": list(sources)}