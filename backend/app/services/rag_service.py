import os
import chromadb
from backend.app.rag.kb_docs import DOCUMENTS
from backend.app.core.config import settings

class RAGService:
    _collection = None
    _fallback_mode = False

    @classmethod
    def initialize(cls):
        """
        Initialize the ChromaDB persistent store and seed the collection.
        If it fails, sets _fallback_mode = True.
        """
        if cls._collection is not None or cls._fallback_mode:
            return

        try:
            # Setup persistent storage path
            persist_dir = os.path.join(os.getcwd(), ".chromadb")
            os.makedirs(persist_dir, exist_ok=True)
            
            client = chromadb.PersistentClient(path=persist_dir)
            cls._collection = client.get_or_create_collection("disaster_medical_guidelines")
            
            # Check if collection is empty
            count = cls._collection.count()
            if count == 0:
                print("Seeding ChromaDB RAG Vector Store...")
                ids = [doc["id"] for doc in DOCUMENTS]
                documents = [doc["content"] for doc in DOCUMENTS]
                metadatas = [{"title": doc["title"], "category": doc["category"]} for doc in DOCUMENTS]
                
                # Chroma DB has a default embedding function (sentence-transformers)
                # If downloading the default model fails or causes an error, it will raise an exception.
                cls._collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"ChromaDB seeded with {len(ids)} guidelines.")
        except Exception as e:
            print(f"ChromaDB initialization failed ({e}). Falling back to Jaccard Similarity.")
            cls._fallback_mode = True

    @classmethod
    def query(cls, query_text: str, limit: int = 2) -> list:
        """
        Query the RAG knowledge base for similar safety / medical documents.
        Falls back to a keyword-overlap Jaccard Similarity search.
        """
        cls.initialize()

        if cls._fallback_mode or cls._collection is None:
            return cls._query_fallback(query_text, limit)

        try:
            results = cls._collection.query(
                query_texts=[query_text],
                n_results=limit
            )
            
            extracted = []
            if results and "documents" in results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    doc_content = results["documents"][0][i]
                    doc_id = results["ids"][0][i]
                    metadata = results["metadatas"][0][i]
                    extracted.append({
                        "id": doc_id,
                        "title": metadata.get("title", "Guideline"),
                        "category": metadata.get("category", "General"),
                        "content": doc_content
                    })
            return extracted
        except Exception as e:
            print(f"ChromaDB query failed ({e}). Running Jaccard search...")
            return cls._query_fallback(query_text, limit)

    @classmethod
    def _query_fallback(cls, query_text: str, limit: int = 2) -> list:
        """
        Jaccard Similarity keyword-matching query fallback.
        Excludes minor stop words to enhance accuracy.
        """
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "is", "are", "of"}
        query_words = set(
            w.strip(".,!?\"'") for w in query_text.lower().split() 
            if w.strip(".,!?\"'") not in stop_words
        )
        
        scored_docs = []
        for doc in DOCUMENTS:
            content_words = set(
                w.strip(".,!?\"'") for w in doc["content"].lower().split()
                if w.strip(".,!?\"'") not in stop_words
            )
            # Calculate Jaccard coefficient: Intersection / Union
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            score = len(intersection) / max(1, len(union))
            
            # Boost score if query keywords appear in the document title
            title_words = set(w.strip(".,!?\"'") for w in doc["title"].lower().split())
            title_match = len(query_words.intersection(title_words))
            score += title_match * 0.1
            
            scored_docs.append((score, doc))
            
        # Sort descending by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Return documents that had some score, or fall back to returning top category matches
        results = [item[1] for item in scored_docs if item[0] > 0]
        if not results:
            # If zero matches, return the first default documents
            results = DOCUMENTS
            
        return results[:limit]
