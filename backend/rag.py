from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from pydantic import BaseModel
import os
import uuid

# Synthetic Telecom Documentation
DOCS = [
    "SOP-101 (Congestion): High PRB utilization (>85%) combined with high latency and packet loss indicates cell congestion. Resolution: Temporarily adjust admission control thresholds and consider offloading traffic to neighboring cells.",
    "SOP-102 (Interference): Low RSRP and low SINR with high drop rates (especially UL RSSI spikes) strongly suggest external RF interference. Resolution: Dispatch field team for RF hunting; adjust antenna tilt to minimize interference footprint.",
    "SOP-103 (Handover Failures): High rate of X2 handover preparation failures indicates neighbor relation issues or misconfigured PCI. Resolution: Audit neighbor lists, verify X2 transport links, and check for PCI confusion.",
    "SOP-104 (Backhaul Degradation): High S1/X2 interface latency and transport SCTP heartbeat failures point to backhaul transport issues. Resolution: Escalate to Transport/Transmission team for microwave/fiber link verification."
]

def setup_rag():
    # Write synthetic docs to a file temporarily
    docs_path = "synthetic_docs.txt"
    with open(docs_path, "w") as f:
        f.write("\n\n".join(DOCS))

    loader = TextLoader(docs_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)

    # Use a lightweight huggingface model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # In-memory Qdrant for development/MVP
    client = QdrantClient(location=":memory:")
    
    qdrant = Qdrant(
        client=client,
        collection_name="telecom_kb",
        embeddings=embeddings
    )
    
    # Check if collection has docs
    try:
        if client.count("telecom_kb").count == 0:
            qdrant.add_documents(docs)
    except:
        qdrant.add_documents(docs)
        
    return qdrant

vector_store = setup_rag()

def search_knowledge_base(query: str, k: int = 2):
    results = vector_store.similarity_search(query, k=k)
    return [{"content": doc.page_content, "source": doc.metadata.get("source", "Knowledge Base")} for doc in results]

if __name__ == "__main__":
    print(search_knowledge_base("high latency and packet loss"))
