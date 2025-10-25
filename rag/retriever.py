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

def get_docs(query: str, history: Optional[list] = None, k: int = 5) -> List[Document]:
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
                # Get recent conversation context (last 2-3 exchanges)
                recent_context = []
                for item in history[-6:]:  # Last 3 exchanges (user + bot)
                    if item.get('role') == 'user' and 'parts' in item:
                        recent_context.append(f"User: {item['parts'][0]}")
                    elif item.get('role') == 'model' and 'parts' in item:
                        # Only include first 100 chars of bot response
                        recent_context.append(f"Bot: {item['parts'][0][:100]}")
                
                # If query is short/vague and we have context, reformulate it
                if len(processed_query.split()) <= 3 and recent_context:
                    from rag.chain import gemini_model
                    if gemini_model:
                        try:
                            reformulation_prompt = f"""Given this conversation context:
{chr(10).join(recent_context)}

The user just asked: "{processed_query}"

This seems like a follow-up question. Reformulate it into a complete, standalone question that includes the necessary context. Keep it concise (under 15 words).

Reformulated question:"""
                            
                            context_aware_query = gemini_model(reformulation_prompt).strip()
                            logger.info(f"Reformulated '{processed_query}' → '{context_aware_query}'")
                        except Exception as e:
                            logger.warning(f"Could not reformulate query: {e}")
                            context_aware_query = processed_query
                
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
            'cse': ['computer science engineering', 'computer science and engineering department', 'CSE department'],
            'ece': ['electronics and communication engineering', 'ECE department'],
            'eee': ['electrical and electronics engineering', 'EEE department'],
            'it': ['information technology', 'IT department'],
            'mba': ['master of business administration', 'MBA department']
        }
        
        # Check for department mentions
        for dept, terms in dept_terms.items():
            if dept.lower() in query.lower():
                enhanced_query = f"{enhanced_query} {' '.join(terms)}"
        
        # Comprehensive topic-specific expansions for intelligent retrieval
        topic_expansions = {
            'placement': [
                'placement statistics', 'placement records', 'companies visited', 'recruitment', 
                'campus placement', 'highest package', 'average package', 'placement cell', 
                'job offers', 'student placement', 'placement training', 'placement drive',
                'placement coordinator', 'placement percentage', 'top recruiters', 'salary packages',
                'placement season', 'placement opportunities', 'corporate tie-ups', 'industry connections'
            ],
            'admission': [
                'admission procedure', 'eligibility criteria', 'how to apply', 'admission process', 
                'entrance exam', 'admission requirements', 'application form', 'admission dates',
                'selection process', 'admission notification', 'document verification', 'seat allocation',
                'counseling process', 'admission helpline', 'online admission', 'admission fee',
                'last date to apply', 'reservation policy', 'admission guidelines', 'intake capacity'
            ],
            'faculty': [
                'faculty members', 'teaching staff', 'professors', 'department head', 'hod name',
                'faculty profile', 'faculty qualification', 'teaching experience', 'faculty expertise',
                'faculty research', 'faculty publications', 'assistant professor', 'associate professor',
                'visiting faculty', 'faculty achievements', 'faculty contact', 'faculty directory'
            ],
            'fee': [
                'fee structure', 'tuition fee', 'course fee', 'total fee', 'fee payment',
                'fee details', 'semester fee', 'annual fee', 'fee breakdown', 'fee concession',
                'scholarship', 'financial aid', 'fee reimbursement', 'payment schedule',
                'fee installments', 'hostel fee', 'transportation fee', 'examination fee',
                'caution deposit', 'refund policy', 'fee waiver', 'fee components'
            ],
            'hostel': [
                'hostel facilities', 'accommodation', 'hostel fee', 'room availability',
                'hostel rules', 'hostel rooms', 'hostel admission', 'mess facility',
                'hostel warden', 'hostel capacity', 'boys hostel', 'girls hostel',
                'hostel amenities', 'room sharing', 'hostel food', 'hostel security',
                'hostel infrastructure', 'residential facilities', 'staying arrangements'
            ],
            'timing': [
                'college timing', 'class schedule', 'working hours', 'college hours', 'time table',
                'academic calendar', 'semester schedule', 'class timings', 'office hours',
                'working days', 'holidays', 'academic session', 'exam schedule',
                'semester duration', 'daily schedule', 'break timings', 'library hours'
            ],
            'facility': [
                'facilities', 'infrastructure', 'laboratory', 'library', 'sports',
                'campus facilities', 'lab facilities', 'library resources', 'computer lab',
                'workshop', 'seminar hall', 'auditorium', 'cafeteria', 'canteen',
                'medical facilities', 'transport facility', 'bus facility', 'wifi',
                'internet facility', 'smart classrooms', 'gym', 'playground', 'recreation',
                'parking', 'banking facilities', 'ATM', 'stationary shop'
            ],
            'course': [
                'course details', 'programs offered', 'branches', 'departments', 'curriculum',
                'syllabus', 'course structure', 'degree programs', 'specialization', 'subjects',
                'course duration', 'credit system', 'electives', 'core subjects', 'course content',
                'academic programs', 'undergraduate courses', 'postgraduate courses', 'diploma courses',
                'course objectives', 'course outcomes', 'course syllabus'
            ],
            'exam': [
                'examination', 'exam schedule', 'exam pattern', 'exam results', 'grading system',
                'internal exams', 'mid-term exams', 'semester exams', 'final exams', 'exam dates',
                'exam hall', 'exam rules', 'exam eligibility', 'exam preparation', 'marks distribution',
                'passing criteria', 'supplementary exams', 'revaluation', 'exam controller'
            ],
            'accreditation': [
                'accreditation', 'NAAC', 'NBA', 'AICTE', 'UGC', 'approval', 'recognition',
                'affiliation', 'certification', 'ranking', 'NIRF', 'rating', 'autonomous status',
                'university affiliation', 'quality rating', 'institutional ranking'
            ],
            'events': [
                'events', 'cultural activities', 'technical fest', 'cultural fest', 'workshops',
                'seminars', 'guest lectures', 'conferences', 'symposium', 'competitions',
                'hackathons', 'sports events', 'annual day', 'tech fest', 'cultural programs',
                'extra-curricular activities', 'student activities', 'club activities'
            ],
            'research': [
                'research', 'research projects', 'research facilities', 'research centers',
                'research publications', 'research papers', 'innovation', 'patents', 'R&D',
                'research scholars', 'PhD programs', 'research funding', 'research collaborations'
            ],
            'contact': [
                'contact', 'address', 'phone number', 'email', 'location', 'contact details',
                'how to reach', 'contact information', 'college address', 'office contact',
                'helpline', 'principal contact', 'admission office contact', 'enquiry'
            ]
        }
        
        # Smart expansion: Add topic-specific terms to enhance query
        for topic in topics:
            if topic in topic_expansions:
                # Add all expansion terms for comprehensive coverage
                enhanced_query = f"{enhanced_query} {' '.join(topic_expansions[topic])}"
                logger.info(f"Applied {topic} expansions for smarter retrieval")
        
        # Expand query with topic-specific terms
        expanded_query = expand_query(enhanced_query, topics)
        
        # Extract and add key phrases
        key_phrases = extract_key_phrases(query)
        if key_phrases:
            expanded_query = f"{expanded_query} {' '.join(key_phrases)}"
            
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
