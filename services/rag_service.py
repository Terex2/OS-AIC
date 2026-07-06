from qdrant_client import QdrantClient, models
from typing import List

class RAGService:
    def __init__(self, host="qdrant", port=6333, collection_name="os_aic_knowledge"):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        try:
            self.client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )
            print(f"Collection '{self.collection_name}' created.")

    def add_document(self, text: str, metadata: dict = None):
        # In a real scenario, text would be embedded first
        # For now, we'll use a dummy vector
        dummy_vector = [0.1] * 1536 # Replace with actual embedding model output
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=hash(text), # Simple hash for ID, replace with UUID in production
                    vector=dummy_vector,
                    payload={"text": text, **(metadata if metadata else {})}
                )
            ]
        )
        print(f"Document added to RAG: {text[:50]}...")

    def search_documents(self, query_text: str, limit: int = 3) -> List[dict]:
        # In a real scenario, query_text would be embedded first
        dummy_query_vector = [0.2] * 1536 # Replace with actual embedding model output
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=dummy_query_vector,
            limit=limit
        )
        return [{
            "text": hit.payload["text"],
            "score": hit.score,
            "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
        } for hit in search_result]

if __name__ == "__main__":
    rag_service = RAGService()
    rag_service.add_document("LangChain هو إطار عمل لتطوير تطبيقات تعتمد على نماذج اللغة الكبيرة.", {"source": "langchain_docs"})
    rag_service.add_document("Ollama يسمح بتشغيل نماذج اللغة الكبيرة محلياً.", {"source": "ollama_docs"})
    
    results = rag_service.search_documents("ما هو Ollama؟")
    print("\nSearch Results:")
    for res in results:
        print(f"- Score: {res["score"]:.2f}, Text: {res["text"]}")
