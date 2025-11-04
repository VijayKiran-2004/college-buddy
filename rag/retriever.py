from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from .embeddings_init import init_embeddings
from .text_processor import preprocess_query
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embeddings and vectordb
embeddings = None
vectordb = None

def init_retriever():
    """Initialize embeddings and vector database with error handling."""
    global embeddings, vectordb
    try:
        embeddings = init_embeddings()
        vectordb = Chroma(
            collection_name="college_buddy",
            embedding_function=embeddings,
            persist_directory="./chroma"
        )
        logger.info("Successfully initialized embeddings and vector database")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings or vector database: {str(e)}")
        raise

# Initialize on module load
init_retriever()

def get_docs(query: str, history: Optional[list] = None, k: int = 3) -> List[Document]:
    """OPTIMIZED: Fast document retrieval with minimal processing."""
    try:
        if not query or not isinstance(query, str):
            return []
        
        # FAST PATH: Just preprocess and search
        processed_query = preprocess_query(query)
        
        if not vectordb:
            logger.error("Vector database not initialized")
            return []
        
        # Direct vector search - no fancy processing
        docs = vectordb.similarity_search(processed_query, k=k)
        logger.info(f"Retrieved {len(docs)} documents for: {processed_query}")
        return docs
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        return []

