"""
Chain of Thought Response Generator
Alternative to Ollama for question answering using RAG results directly
"""

import re
from typing import List, Dict, Optional


class ChainOfThoughtGenerator:
    """
    Generates answers without requiring Ollama.
    Uses the retrieved documents directly to construct intelligent responses.
    """
    
    def __init__(self):
        self.confidence_threshold = 0.3
        
    def generate(self, query: str, documents: List[Dict], 
                 history_context: str = "") -> str:
        """
        Generate response using chain-of-thought approach
        
        Args:
            query: User's question
            documents: Retrieved relevant documents
            history_context: Previous conversation context
            
        Returns:
            Generated answer string
        """
        
        if not documents:
            return self._handle_no_documents(query)
        
        # Classify query type
        query_type = self._classify_query(query)
        
        # Generate response based on type
        if query_type == "person":
            return self._answer_person_query(query, documents)
        elif query_type == "timing":
            return self._answer_timing_query(query, documents)
        elif query_type == "admission":
            return self._answer_admission_query(query, documents)
        elif query_type == "contact":
            return self._answer_contact_query(query, documents)
        else:
            return self._answer_general_query(query, documents)
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        person_keywords = ['who', 'hod', 'principal', 'director', 'dean', 
                          'registrar', 'founder', 'staff', 'teacher', 'professor']
        timing_keywords = ['timing', 'time', 'schedule', 'hours', 'when', 'during']
        admission_keywords = ['admission', 'enroll', 'apply', 'criteria', 'cutoff',
                             'merit', 'eligibility', 'intake', 'seats']
        contact_keywords = ['contact', 'phone', 'email', 'address', 'office', 'reach']
        
        if any(kw in query_lower for kw in person_keywords):
            return "person"
        elif any(kw in query_lower for kw in timing_keywords):
            return "timing"
        elif any(kw in query_lower for kw in admission_keywords):
            return "admission"
        elif any(kw in query_lower for kw in contact_keywords):
            return "contact"
        else:
            return "general"
    
    def _handle_no_documents(self, query: str) -> str:
        """Handle case when no documents are retrieved"""
        query_type = self._classify_query(query)
        
        responses = {
            "person": "I don't have information about this person in our database. Please contact the college administration directly.",
            "timing": "I don't have the specific timing information available. Please contact the college office or check the academic calendar.",
            "admission": "I don't have specific admission details available. Please contact the Admissions Office directly.",
            "contact": "I don't have the contact information you're looking for. Please visit the college website or contact the main office.",
            "general": "I couldn't find information about that in my knowledge base. Please contact the college directly for accurate information."
        }
        
        return responses.get(query_type, responses["general"])
    
    def _answer_person_query(self, query: str, documents: List[Dict]) -> str:
        """Answer questions about people"""
        # Extract names from documents - look for "Dr." pattern or key titles
        names_found = []
        detailed_info = []
        
        for doc in documents[:8]:  # Check more documents
            text = doc['text']
            
            # Look for Dr./Prof. patterns with names
            if 'Dr.' in text or 'Prof.' in text:
                # Extract sentences with Dr./Prof.
                sentences = text.split('.')
                for sentence in sentences:
                    if 'Dr.' in sentence or 'Prof.' in sentence:
                        cleaned = sentence.strip()
                        # Keep complete sentences without truncation
                        if len(cleaned) > 20:  # Only filter out very short fragments
                            detailed_info.append(cleaned)
            
            # Look for HOD/Head patterns
            if ('Head' in text and 'Department' in text) or 'HOD' in text:
                if len(text) > 50:
                    # Keep complete text without truncation
                    detailed_info.append(text)
            
            # Look for Principal patterns
            if 'Principal' in text and len(text) > 50:
                # Keep complete text without truncation
                detailed_info.append(text)
        
        if detailed_info:
            response = "Based on our college records:\n\n"
            # Deduplicate and limit to top 3 most relevant
            unique_info = list(dict.fromkeys(detailed_info))[:3]
            for info in unique_info:
                response += f"• {info}\n\n"
            return response.strip()
        
        # Fallback: use top documents
        if documents:
            response_parts = ["Based on available information:\n\n"]
            for doc in documents[:2]:
                text = doc['text'].strip()
                if len(text) > 50:  # Only use meaningful text
                    # Show complete text without truncation
                    response_parts.append(f"• {text}\n")
            
            response = "".join(response_parts).strip()
            if response != "Based on available information:\n":
                return response
        
        return "I don't have specific information about this person. Please contact the college administration."
    
    def _answer_timing_query(self, query: str, documents: List[Dict]) -> str:
        """Answer timing-related questions"""
        response_parts = ["Here's the timing information:\n\n"]
        
        # Extract timing information
        has_content = False
        for doc in documents[:3]:
            text = doc['text']
            if any(kw in text.lower() for kw in ['timing', 'time', 'schedule', 'hours', ':', 'am', 'pm']):
                response_parts.append(f"• {text.strip()}\n")
                has_content = True
        
        if not has_content:
            response_parts = ["Based on available information:\n\n"]
            for doc in documents[:2]:
                response_parts.append(f"• {doc['text'][:150].strip()}...\n")
        
        response = "".join(response_parts).strip()
        response += "\n\nFor the most current schedule, please contact the college office or check the academic calendar."
        
        return response
    
    def _answer_admission_query(self, query: str, documents: List[Dict]) -> str:
        """Answer admission-related questions"""
        response_parts = ["Here's what I found about admissions:\n\n"]
        
        for i, doc in enumerate(documents[:4], 1):
            text = doc['text'].strip()
            response_parts.append(f"• {text}\n")
        
        response = "".join(response_parts).strip()
        
        if response == "Here's what I found about admissions:\n":
            return "I don't have detailed admission information. Please contact the Admissions Office at the college."
        
        response += "\n\nFor more information or to apply, please visit the college website or contact the Admissions Office."
        return response
    
    def _answer_contact_query(self, query: str, documents: List[Dict]) -> str:
        """Answer contact-related questions"""
        response_parts = ["Here's the contact information:\n\n"]
        
        for doc in documents[:3]:
            text = doc['text'].strip()
            response_parts.append(f"• {text}\n")
        
        response = "".join(response_parts).strip()
        
        if response == "Here's the contact information:\n":
            return "I don't have the contact information readily available. Please check the college website for contact details."
        
        return response
    
    def _answer_general_query(self, query: str, documents: List[Dict]) -> str:
        """Answer general questions"""
        response_parts = []
        
        # Add introductory phrase
        response_parts.append("Here's what I found:\n\n")
        
        # Add top 3 documents as bullet points
        for i, doc in enumerate(documents[:3], 1):
            text = doc['text'].strip()
            # Limit text length to 200 chars per point
            if len(text) > 200:
                text = text[:200].rsplit(' ', 1)[0] + "..."
            response_parts.append(f"• {text}\n")
        
        response = "".join(response_parts).strip()
        
        # Add helpful closing
        response += "\n\nIf you need more details, please feel free to ask or contact the relevant department at the college."
        
        return response
    
    def answer_from_context(self, query: str, context: str) -> str:
        """
        Simple context-based answer generation
        When RAG retrieval already provides good context
        """
        if not context or context.strip() == "":
            return "I couldn't find relevant information for your query. Please try a different question or contact the college directly."
        
        # Simple response that quotes context
        return f"Based on our knowledge base:\n\n{context}\n\nIf you need more information, please contact the college directly."


class SimpleRAGResponder:
    """
    Very simple responder that works with just RAG results
    No LLM required
    """
    
    def __init__(self):
        self.generator = ChainOfThoughtGenerator()
    
    def respond(self, query: str, retrieved_documents: List[Dict], 
                reranked_documents: Optional[List[Dict]] = None) -> str:
        """
        Generate response from retrieved documents
        
        Args:
            query: User's question
            retrieved_documents: Initial retrieved documents
            reranked_documents: Optionally reranked documents (higher priority)
            
        Returns:
            Generated response
        """
        
        # Use reranked if available, otherwise use retrieved
        docs_to_use = reranked_documents if reranked_documents else retrieved_documents
        
        if not docs_to_use:
            return self.generator._handle_no_documents(query)
        
        # Generate response
        return self.generator.generate(query, docs_to_use[:5])  # Use top 5 docs


def create_response_without_ollama(query: str, documents: List[Dict], 
                                  history: str = "") -> str:
    """
    Standalone function to generate responses without Ollama
    
    Usage:
        response = create_response_without_ollama(
            "Who is the principal?",
            retrieved_docs,
            history_context
        )
    """
    generator = ChainOfThoughtGenerator()
    return generator.generate(query, documents, history)
