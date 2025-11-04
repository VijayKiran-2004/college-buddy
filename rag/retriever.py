from typing import List, Dict, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from .embeddings_init import init_embeddings
from .text_processor import preprocess_query, detect_topics, expand_query, extract_key_phrases
import logging

# Define common abbreviations used in the college context
ABBREVIATION_MAP: Dict[str, str] = {
    "tkr": "Teegala Krishna Reddy",
    "tkrcet": "Teegala Krishna Reddy College of Engineering and Technology",
    "cse": "Computer Science and Engineering",
    "ece": "Electronics and Communication Engineering",
    "eee": "Electrical and Electronics Engineering",
    "it": "Information Technology",
    "ai": "Artificial Intelligence",
    "ml": "Machine Learning",
    "csd": "Computer Science and Design",
    "mba": "Master of Business Administration"
}

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
    """
    Enhanced document retrieval with NLP processing and error handling.
    
    Args:
        query (str): The user's query
        history (list): Conversation history
        k (int): Number of documents to retrieve
        
    Returns:
        List[Document]: Retrieved documents
    """
    try:
        if not query or not isinstance(query, str):
            logger.warning(f"Invalid query type: {type(query)}")
            return []
            
        # Process the current query
        processed_query = preprocess_query(query)
        
        # Detect topics in the query
        topics = detect_topics(processed_query)
        logger.info(f"Detected topics: {topics}")
        
        # Process conversation history for context-aware queries
        history_queries = []
        context_aware_query = processed_query
        
        if history and len(history) >= 2:
            try:
                # Check if user is responding to a clarification question
                # (If so, skip vague query reformulation as chain.py will handle it)
                is_clarification_response = False
                if len(history) >= 1 and history[-1].get("role") == "model":
                    last_bot_msg = history[-1].get("parts", [""])[0]
                    clarification_indicators = [
                        "what specifically would you like to know",
                        "are you interested in",
                        "would you like to know about",
                        "which one",
                        "please specify",
                        "can you clarify"
                    ]
                    is_clarification_response = any(
                        indicator in last_bot_msg.lower() 
                        for indicator in clarification_indicators
                    )
                
                # Get recent conversation context (last 2-3 exchanges)
                recent_context = []
                for item in history[-6:]:  # Last 3 exchanges (user + bot)
                    if item.get('role') == 'user' and 'parts' in item:
                        recent_context.append(f"User: {item['parts'][0]}")
                    elif item.get('role') == 'model' and 'parts' in item:
                        # Only include first 150 chars of bot response
                        recent_context.append(f"Bot: {item['parts'][0][:150]}")
                
                # Check if query is vague/needs context (expanded detection)
                vague_queries = [
                    'programs', 'courses', 'faculty', 'facilities', 'labs', 'placements',
                    'admissions', 'fees', 'scholarship', 'hostel', 'research', 'projects',
                    'offered', 'available', 'members', 'details', 'information', 'about',
                    'how many', 'total', 'number'
                ]
                
                is_vague = (
                    len(processed_query.split()) <= 5 or  # Increased from 3 to 5 words
                    any(word in processed_query.lower() for word in vague_queries)
                )
                
                # Only reformulate if:
                # 1. Query is vague AND
                # 2. We have context AND
                # 3. User is NOT responding to a clarification (chain.py handles that)
                if is_vague and recent_context and not is_clarification_response:
                    # OPTIMIZED: Use simple concatenation instead of LLM call
                    # Extract last user query from context
                    last_user_query = None
                    for ctx in reversed(recent_context):
                        if ctx.startswith("User:"):
                            last_user_query = ctx.replace("User:", "").strip()
                            break
                    
                    if last_user_query and last_user_query.lower() != processed_query.lower():
                        # Simple concatenation for context
                        context_aware_query = f"{last_user_query} {processed_query}"
                        logger.info(f"Context-aware query: '{context_aware_query}'")
                    else:
                        context_aware_query = processed_query
                elif is_clarification_response:
                    logger.info(f"Skipping reformulation - user responding to clarification")
                
                history_queries = [
                    preprocess_query(item['parts'][0]) 
                    for item in history[-5:] 
                    if item.get('role') == 'user' and 'parts' in item
                ]
            except Exception as he:
                logger.warning(f"Error processing history: {str(he)}")
        
        # Create enhanced query (use reformulated if available)
        enhanced_query = context_aware_query
        if history_queries and context_aware_query == processed_query:
            # Only concatenate if we didn't reformulate
            enhanced_query = f"{' '.join(history_queries[-2:])} {enhanced_query}"
        
        # Add department-specific terms
        dept_terms = {
            'cse': ['computer science engineering', 'computer science and engineering department', 'CSE department', 'CSE HOD', 'computer science head'],
            'ece': ['electronics and communication engineering', 'ECE department', 'ECE HOD', 'electronics communication head'],
            'eee': ['electrical and electronics engineering', 'EEE department', 'EEE HOD', 'electrical electronics head'],
            'it': ['information technology', 'IT department', 'IT HOD', 'information technology head', 'Dr. N. Satya Narayana', 'Satya Narayana', 'it@tkrcet.com', '8498085217'],
            'mba': ['master of business administration', 'MBA department', 'MBA HOD', 'management head'],
            'civil': ['civil engineering', 'civil department', 'civil HOD', 'Dr. K. Satya Sai', 'civil@tkrcet.com', '8498085212'],
            'mech': ['mechanical engineering', 'mechanical department', 'mech HOD', 'D Rushi Kumar Reddy', 'mech@tkrcet.com', '8498085214']
        }
        
        # Check for department mentions and HOD queries
        is_hod_query = any(word in query.lower() for word in ['hod', 'head of department', 'head of', 'department head'])
        
        for dept, terms in dept_terms.items():
            if dept.lower() in query.lower():
                if is_hod_query:
                    # For HOD queries, add contact information terms
                    enhanced_query = f"{enhanced_query} {' '.join(terms)} contact information phone email"
                else:
                    enhanced_query = f"{enhanced_query} {' '.join(terms)}"
        
        # OPTIMIZED: Simplified topic expansions - only essential terms for faster processing
        topic_expansions = {
            'placement': ['placement statistics', 'companies', 'packages'],
            'admission': ['admission procedure', 'eligibility', 'how to apply'],
            'faculty': ['faculty', 'professor', 'HOD', 'head of department'],
            'fee': ['fee structure', 'tuition fee', 'scholarship'],
            'hostel': ['hostel facilities', 'accommodation'],
            'timing': ['college timing', 'working hours', 'schedule'],
            'facility': ['facilities', 'infrastructure', 'lab', 'library'],
            'course': ['course details', 'programs', 'branches', 'curriculum'],
            'exam': ['examination', 'exam schedule', 'results'],
            'accreditation': ['accreditation', 'NAAC', 'NBA', 'AICTE'],
            'events': ['events', 'fest', 'workshops', 'seminars'],
            'research': ['research', 'projects', 'publications'],
            'contact': ['contact', 'phone', 'email', '@tkrcet.com']
        }
        
        # Smart expansion: Add only 3 most relevant terms per topic for speed
        for topic in topics:
            if topic in topic_expansions:
                # Take only first 3 expansion terms to keep query lightweight
                enhanced_query = f"{enhanced_query} {' '.join(topic_expansions[topic][:3])}"
        
        # OPTIMIZED: Skip expand_query and extract_key_phrases for faster processing
        expanded_query = enhanced_query

            
        logger.info(f"Enhanced query: {expanded_query}")
        
        # Perform vector search
        if not vectordb:
            logger.error("Vector database not initialized")
            return []
            
        try:
            # If query is about HOD, faculty, or department staff, prioritize department pages
            is_faculty_query = any(term in query.lower() for term in ['hod', 'head of department', 'faculty', 'professor', 'staff', 'team'])
            
            # Check for department mentions with word boundaries
            query_words = query.lower().split()
            dept_mentioned = any(dept in query_words or f'{dept}' in query.lower() for dept in ['cse', 'ece', 'eee', 'mba', 'civil', 'mech', 'mechanical', 'aiml', 'csd'])
            # Special handling for 'it' to avoid matching 'it' in other words
            if 'it' in query_words or ' it ' in f' {query.lower()} ' or query.lower().startswith('it ') or query.lower().endswith(' it'):
                dept_mentioned = True
            # Check for multi-word department names
            if any(name in query.lower() for name in ['data science', 'artificial intelligence', 'machine learning']):
                dept_mentioned = True
            
            is_dept_query = dept_mentioned
            
            if is_faculty_query and is_dept_query:
                # Identify which department
                dept_urls = {
                    'cse': 'computer-science-engineering',
                    'ece': 'electronics-communication-engineering', 
                    'eee': 'electrical-electronics-engineering',
                    'it': 'information-technology',
                    'mba': 'mba',
                    'civil': 'civil-engineering',
                    'mech': 'mechanical-engineering',
                    'mechanical': 'mechanical-engineering',
                    'aiml': 'artificial-intelligence-and-machine-learning',
                    'ai': 'artificial-intelligence-and-machine-learning',
                    'ml': 'artificial-intelligence-and-machine-learning',
                    'csd': 'cse-allied-ds',
                    'data science': 'cse-allied-ds',
                    'ds': 'cse-allied-ds'
                }
                
                dept_name = None
                for dept_key, url_part in dept_urls.items():
                    if dept_key in query.lower():
                        dept_name = url_part
                        break
                
                # Get ALL documents from database and manually filter
                all_docs_data = vectordb.get()
                
                # Find documents from the specific department
                dept_doc_indices = []
                for i in range(len(all_docs_data['ids'])):
                    source = all_docs_data['metadatas'][i].get('source', '')
                    if dept_name and dept_name in source:
                        dept_doc_indices.append(i)
                
                # Create Document objects from the matched indices
                from langchain_core.documents import Document as LCDocument
                dept_documents = [
                    LCDocument(
                        page_content=all_docs_data['documents'][i],
                        metadata=all_docs_data['metadatas'][i]
                    )
                    for i in dept_doc_indices
                ]
                
                # Prioritize chunks that contain HOD-related keywords
                hod_keywords = ['head of department', 'head of the department', 'hod', 'vice principal', 'dean']
                hod_docs = []
                other_dept_docs = []
                
                for doc in dept_documents:
                    content_lower = doc.page_content.lower()
                    if any(keyword in content_lower for keyword in hod_keywords):
                        hod_docs.append(doc)
                    else:
                        other_dept_docs.append(doc)
                
                # Reorder: HOD-related chunks first
                dept_documents = hod_docs + other_dept_docs
                
                # Also get semantic search results
                semantic_docs = vectordb.similarity_search(expanded_query, k=k)
                
                # Combine: department docs first (up to 5), then semantic results
                source_docs = dept_documents[:5] + [d for d in semantic_docs if d not in dept_documents][:k-len(dept_documents[:5])]
                
                logger.info(f"Faculty query for {dept_name}: Found {len(hod_docs)} HOD docs, {len(dept_documents)} total dept docs")
            else:
                source_docs = vectordb.max_marginal_relevance_search(expanded_query, k=k, fetch_k=20)
                
            logger.info(f"Retrieved {len(source_docs)} documents")
            return source_docs
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            return []
            
    except Exception as e:
        logger.error(f"Error in document retrieval: {str(e)}")
        return []

    expanded_query = expand_abbreviations(full_query)
    source_docs = vectordb.similarity_search(expanded_query, k=k)
    new_docs = []
    for d in source_docs:
        url   = d.metadata["source"]
        title = d.metadata["title"]
        head  = (d.metadata.get("heading") or "").replace(" ","-")
        updated_time = d.metadata.get('last_scraped', 'N/A')[:16]
        new_content = d.page_content + f"\n\nNavigate: [{title}]({url}#{head}) (updated {updated_time})"
        new_docs.append(
            Document(page_content=new_content, metadata=d.metadata)
        )
    return new_docs
