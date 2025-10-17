import os
import time
import threading
import PyPDF2
import chromadb
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class KnowledgeFileHandler(FileSystemEventHandler):
    def __init__(self, engine):
        self.engine = engine
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.pdf', '.txt', '.md')):
            self.engine._process_file(event.src_path)

class KnowledgeEngine(threading.Thread):
    def __init__(self, knowledge_base_path, data_path, model_manager=None):
        super().__init__()
        self.daemon = True
        self.knowledge_base_path = knowledge_base_path
        self.model_manager = model_manager
        self.stop_event = threading.Event()
        
        # Vector store
        vector_store_path = os.path.join(data_path, "vector_store")
        self.client = chromadb.PersistentClient(path=vector_store_path)
        self.collection = self.client.get_or_create_collection("enterprise_knowledge")
        
        # Load existing indexed files from ChromaDB
        self.indexed_files = set()
        self._load_existing_files()
        
        # File system watcher
        self.observer = Observer()
        self.handler = KnowledgeFileHandler(self)
        
        print(f"[KnowledgeEngine] Collective Consciousness online. {len(self.indexed_files)} files already indexed.")

    def _load_existing_files(self):
        """Load existing document IDs from ChromaDB to prevent duplicates"""
        try:
            existing = self.collection.get()
            if existing and existing['metadatas']:
                for metadata in existing['metadatas']:
                    if 'source' in metadata:
                        self.indexed_files.add(metadata['source'])
        except Exception as e:
            print(f"[KnowledgeEngine] Warning: Could not load existing files: {e}")

    def run(self):
        # Start file system watcher (with duplicate prevention)
        try:
            self.observer.schedule(self.handler, self.knowledge_base_path, recursive=True)
            self.observer.start()
        except RuntimeError as e:
            if "already scheduled" in str(e):
                print(f"[KnowledgeEngine] Watcher already active for {self.knowledge_base_path}")
            else:
                raise e
        
        # Initial scan for new files
        try:
            self._initial_scan()
        except Exception as e:
            print(f"[KnowledgeEngine] Initial scan error: {e}")
        
        # Keep running
        while not self.stop_event.is_set():
            try:
                time.sleep(10)
            except Exception as e:
                print(f"[KnowledgeEngine] Runtime error: {e}")
                continue

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.stop_event.set()

    def _initial_scan(self):
        """Scan for files not yet indexed"""
        for root, _, files in os.walk(self.knowledge_base_path):
            for file in files:
                if file.endswith(('.pdf', '.txt', '.md')):
                    file_path = os.path.join(root, file)
                    if file_path not in self.indexed_files:
                        self._process_file(file_path)

    def _process_file(self, file_path):
        """Process and index a single file"""
        try:
            domain = self._get_domain(file_path)
            content = self._read_file(file_path)
            if not content:
                return
            
            # Chunk content
            chunks = self._chunk_content(content)
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                summary, keywords = self._analyze_chunk(chunk)
                doc_id = f"{file_path}_{i}"
                
                self.collection.add(
                    documents=[chunk],
                    metadatas=[{
                        "source": file_path,
                        "domain": domain,
                        "chunk": i,
                        "filename": os.path.basename(file_path),
                        "summary": summary,
                        "keywords": keywords
                    }],
                    ids=[doc_id]
                )
            
            self.indexed_files.add(file_path)
            print(f"[KnowledgeEngine] Indexed {len(chunks)} chunks from {os.path.basename(file_path)} ({domain})")
            
        except Exception as e:
            print(f"[KnowledgeEngine] Error processing {file_path}: {e}")

    def _get_domain(self, file_path):
        """Extract domain from file path"""
        rel_path = os.path.relpath(file_path, self.knowledge_base_path)
        return rel_path.split(os.sep)[0] if os.sep in rel_path else "general"

    def _chunk_content(self, content, chunk_size=800, overlap=100):
        """Split content into overlapping chunks"""
        chunks = []
        for i in range(0, len(content), chunk_size - overlap):
            chunk = content[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def _analyze_chunk(self, chunk):
        """Use LLM to analyze chunk for summary and keywords"""
        if not self.model_manager:
            print("[KnowledgeEngine] WARNING: No model_manager - using fallback analysis")
            return chunk[:100] + "...", "general"
        
        try:
            llm = self.model_manager.get_model("general_purpose")
            print(f"[KnowledgeEngine] Using LLM model: {type(llm).__name__}")
            
            prompt = f"Analyze this text and provide: 1) A concise summary (max 100 chars), 2) Key topics (comma-separated):\n\n{chunk[:500]}"
            
            response = llm.generate(prompt)
            lines = response.split('\n')
            summary = lines[0][:100] if lines else chunk[:100]
            keywords = lines[1] if len(lines) > 1 else "general"
            
            print(f"[KnowledgeEngine] LLM Analysis - Summary: {summary[:50]}... Keywords: {keywords}")
            return summary, keywords
            
        except Exception as e:
            print(f"[KnowledgeEngine] LLM analysis failed: {e}")
            return chunk[:100] + "...", "general"

    def _read_file(self, file_path):
        """Read content from file"""
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return '\n'.join(page.extract_text() or "" for page in reader.pages)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            print(f"[KnowledgeEngine] Error reading {file_path}: {e}")
            return None

    def query(self, query_text, n_results=5, domain=None):
        """Query the knowledge base"""
        query_params = {
            "query_texts": [query_text],
            "n_results": n_results
        }
        
        # Only add where clause if domain is specified
        if domain:
            query_params["where"] = {"domain": domain}
        
        results = self.collection.query(**query_params)
        return results['documents'][0] if results and results['documents'] else []

    def get_stats(self):
        """Get knowledge base statistics"""
        return {
            "total_documents": self.collection.count(),
            "indexed_files": len(self.indexed_files),
            "domains": len([d for d in os.listdir(self.knowledge_base_path) if os.path.isdir(os.path.join(self.knowledge_base_path, d))])
        }
