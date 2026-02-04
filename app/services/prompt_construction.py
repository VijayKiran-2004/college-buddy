"""
Prompt construction module for the college chatbot.
Handles building context-aware prompts with relaxed strictness for better user experience.
"""


def build_context_prompt(query, documents, history_context=""):
    """
    Build a relaxed, helpful prompt for the college chatbot.
    
    This version prioritizes helpfulness while maintaining accuracy.
    It's less strict about missing information.
    
    Args:
        query: User's question
        documents: Retrieved context documents
        history_context: Previous conversation history
        
    Returns:
        Formatted prompt string
    """
    
    # Check if this is a person query
    person_keywords = ['who', 'hod', 'principal', 'director', 'dean', 'registrar', 'founder', 'head', 'staff', 'teacher', 'professor']
    is_person_query = any(kw in query.lower() for kw in person_keywords)
    
    if not documents:
        context = "No relevant information found in the knowledge base."
        has_context = False
    else:
        context = "\n".join([f"• {doc['text']}" for doc in documents[:4]])  # Show complete documents
        has_context = True

    history_text = ""
    if history_context:
        history_text = f"\nRecent conversation:\n{history_context}\n"

    # Optimized prompt - concise, relevant, and focused
    prompt = f"""You are a helpful TKRCET College Assistant.

{history_text}
Available Information:
{context}

Student's Question: {query}

INSTRUCTIONS:
1. Answer the question using the information provided above
2. Synthesize a helpful response from the available context
3. Keep response to 2-5 sentences - be concise but complete
4. Extract and use any relevant details from the context
5. If the context contains useful information, use it to form your answer
6. Be helpful and informative - provide value to the student
7. For admission/facilities/courses: summarize key points from the context

Answer:"""
    
    return prompt
    
    return prompt


def build_person_query_prompt(query, documents, history_context=""):
    """
    Specialized prompt for queries about people (Principal, HOD, staff, etc.)
    More helpful with available context.
    """
    
    if not documents:
        context_info = "No information available"
        has_context = False
    else:
        context_info = "\n".join([f"• {doc['text']}" for doc in documents[:5]])  # Show complete documents for person queries
        has_context = True

    history_text = ""
    if history_context:
        history_text = f"\nPrevious messages:\n{history_context}\n"

    prompt = f"""You are a helpful TKRCET College Assistant.

{history_text}
Available Information About People/Staff:
{context_info}

Question: {query}

CRITICAL Instructions:
1. Answer ONLY the specific question asked about the person/role
2. ONLY use names and details that appear in the "Available Information About People/Staff" section above
3. DO NOT make up or invent any names - if you don't see a name above, say you don't have that information
4. CAREFULLY READ the context and extract the exact name with title (Dr., Prof., etc.)
5. If you find a name with "Head", "Principal", "Dean", "HOD", or similar title, QUOTE IT EXACTLY
6. Provide the person's full name, designation, and relevant details FROM THE CONTEXT ONLY
7. Keep response to 2-3 sentences - be concise and direct
8. If no relevant person is mentioned in the context above, say: "I don't have specific details about this person. Please contact the college administration."
9. NEVER mention unrelated people or topics from the context
10. Be precise and factual - no filler phrases

Response:"""

    return prompt


def build_general_prompt(query, documents, history_context=""):
    """
    General purpose prompt for regular college queries.
    Balanced between helpfulness and accuracy.
    """
    
    if not documents:
        context = "No relevant documents found."
    else:
        context = "\n".join([f"• {doc['text']}" for doc in documents[:5]])  # Show complete documents

    history_text = ""
    if history_context:
        history_text = f"\nContext from previous chat:\n{history_context}\n"

    prompt = f"""You are a helpful TKRCET College Assistant.

Your purpose is to answer questions about college admissions, courses, facilities, campus life, and general information.

{history_text}
Available Information:
{context}

Question: {query}

Instructions:
1. Answer based on the information provided above
2. If the answer is in the context, provide it directly
3. If you need more details but have partial information, provide what you know
4. If information is completely missing, suggest contacting the relevant department
5. Be helpful, clear, and informative
6. Use bullet points for lists when helpful

Response:"""

    return prompt
