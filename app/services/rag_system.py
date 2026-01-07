"""
Unified RAG System with Conversation Memory and Query Clarity Detection
Uses Ollama Gemma 3 1B model with FAISS vector search
Enhanced with Query Expansion, Multi-Query Retrieval, and Smart Abbreviation Handling
"""

import json
import faiss
import numpy as np
import requests
import random
import sys
import os
from sentence_transformers import SentenceTransformer, CrossEncoder
from collections import deque
import re
from rank_bm25 import BM25Okapi
from .faiss_cache import load_faiss_index, save_faiss_index
from .bm25_cache import load_bm25_index, save_bm25_index

# Fix Windows encoding
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class RAGSystem:
    """Unified RAG system with context awareness and clarity detection"""
    
    def __init__(
        self,
        chunks_path='app/database/vectordb/unified_vectors.json',
        embedding_model='all-MiniLM-L6-v2',
        cross_encoder_model='cross-encoder/ms-marco-MiniLM-L-6-v2',
        ollama_model='gemma3:1b',  # Using gemma3:1b - lower memory, better reliability
        ollama_url='http://localhost:11434/api/generate',
        max_history=5,
        faiss_cache_path='app/database/vectordb/faiss_index.bin',
        bm25_cache_path='app/database/vectordb/bm25_index.pkl'
    ):
        print("Initializing RAG System...")
        
        with open(chunks_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        print(f"✓ Loaded {len(self.chunks)} chunks")
        
        self.embedding_model = SentenceTransformer(embedding_model)
        print(f"✓ Loaded embedding model: {embedding_model}")
        
        self.cross_encoder = CrossEncoder(cross_encoder_model)
        print(f"✓ Loaded cross encoder: {cross_encoder_model}")
        
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url
        
        # FAISS Index Caching
        self.index = load_faiss_index(faiss_cache_path)
        if self.index:
            print(f"✓ Loaded FAISS index from cache: {faiss_cache_path}")
        else:
            print("Building FAISS index...")
            embeddings = self.embedding_model.encode([c['text'] for c in self.chunks], convert_to_tensor=True)
            embeddings_np = embeddings.cpu().detach().numpy().astype(np.float32)
            self.index = faiss.IndexFlatL2(embeddings_np.shape[1])
            self.index.add(embeddings_np)
            save_faiss_index(self.index, faiss_cache_path)
            print(f"✓ FAISS index built and cached with dimension: {embeddings_np.shape[1]}")
        
        # BM25 Index Caching
        self.bm25 = load_bm25_index(bm25_cache_path)
        if self.bm25:
            print(f"✓ Loaded BM25 index from cache: {bm25_cache_path}")
        else:
            print("Building BM25 index...")
            corpus = [c['text'] for c in self.chunks]
            tokenized_corpus = [doc.lower().split() for doc in corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            save_bm25_index(self.bm25, bm25_cache_path)
            print(f"✓ BM25 index built and cached")
        
        # Conversation history for context awareness
        self.conversation_history = deque(maxlen=max_history)
        
        # Unclear query patterns
        self.unclear_keywords = ['what', 'how', 'why', 'which', 'tell me', 'show me']
        self.ollama_available = False  # Track Ollama availability
        
        # Lazy import chain responder to avoid circular imports
        try:
            from .chain import SimpleRAGResponder
            self.chain_responder = SimpleRAGResponder()  # Fallback responder
        except ImportError:
            self.chain_responder = None
        
        self._test_connection()

    def _test_connection(self):
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.ollama_model, "prompt": "test", "stream": False},
                timeout=180  # Increased timeout to handle model loading and generation
            )
            if response.status_code == 200:
                print(f"✓ Connected to Ollama: {self.ollama_model}")
                self.ollama_available = True
            else:
                print(f"⚠ Ollama returned status {response.status_code}")
                print(f"   Using fallback response generator (no LLM)")
                self.ollama_available = False
        except Exception as e:
            print(f"⚠ Ollama connection error: {str(e)}")
            print(f"   Using fallback response generator (no LLM)")
            self.ollama_available = False

    def _is_query_clear(self, query):
        """Detect if query is too vague or too generic - LENIENT MODE"""
        query_lower = query.lower()
        words = query_lower.split()
        
        # Too short = unclear
        if len(words) < 1:
            return False
        
        # Extended comprehensive list of college-related terms
        college_keywords = [
            # Academic
            'admission', 'course', 'program', 'major', 'minor', 'specialization', 'subject',
            'curriculum', 'syllabus', 'elective', 'mandatory', 'semester', 'exam', 'test',
            'assignment', 'project', 'thesis', 'dissertation', 'degree', 'certificate', 'diploma',
            
            # People/Leadership
            'principal', 'director', 'chairman', 'chancellor', 'rector', 'founder', 'president',
            'dean', 'registrar', 'secretary', 'professor', 'faculty', 'instructor', 'lecturer',
            'staff', 'teacher', 'mentor', 'advisor', 'counselor',
            
            # Campus/Facilities
            'college', 'university', 'tkrcet', 'campus', 'facility', 'building', 'classroom',
            'laboratory', 'lab', 'library', 'infrastructure', 'infrastructure', 'hostel',
            'dormitory', 'mess', 'cafeteria', 'transport', 'bus', 'wifi', 'parking',
            'medical', 'health', 'counseling', 'clinic',
            
            # Admissions/Enrollment
            'apply', 'application', 'admit', 'enrollment', 'register', 'registration',
            'requirement', 'eligibility', 'criteria', 'cutoff', 'rank', 'merit', 'quota',
            'category', 'reservation', 'eamcet', 'eapcet', 'ece', 'cet',
            
            # Fees/Finance
            'fee', 'cost', 'tuition', 'payment', 'scholarship', 'financial', 'aid',
            'loan', 'refund', 'waiver', 'discount',
            
            # Academics/Learning
            'academic', 'training', 'internship', 'placement', 'job', 'career',
            'practical', 'theory', 'lab', 'workshop', 'seminar', 'conference',
            
            # Schedule/Timing
            'timing', 'schedule', 'class', 'session', 'semester', 'year', 'batch',
            'semester', 'holiday', 'vacation', 'break',
            
            # General college interest
            'activity', 'club', 'sports', 'event', 'cultural', 'technical',
            'committee', 'society', 'association', 'competition'
        ]
        
        # Pattern-based detection - questions about college
        question_patterns = ['who', 'what', 'when', 'where', 'why', 'how', 'is', 'are', 'do', 'does', 'can', 'will']
        has_question_pattern = any(pattern in query_lower for pattern in question_patterns)
        
        # Check for college-related content
        has_college_keyword = any(kw in query_lower for kw in college_keywords)
        
        # Single word: must be college-related keyword
        if len(words) == 1:
            return has_college_keyword
        
        # Two words: if has college keyword OR is a question, it's clear
        if len(words) == 2:
            return has_college_keyword or has_question_pattern
        
        # Three+ words: generally clear unless it's random gibberish
        if len(words) >= 3:
            # Check if it looks like a genuine question/statement
            if has_college_keyword:
                return True
            # If it's a question pattern with reasonable length
            if has_question_pattern and len(query) > 8:
                return True
        
        # Default: unclear
        return False

    def _ask_clarification(self, query):
        """Generate clarification questions for unclear queries"""
        clarifications = [
            f"Your question seems a bit vague. Could you be more specific about what you want to know? For example, are you asking about admissions, courses, or facilities?",
            f"I want to help better. Could you provide more details? For instance, are you interested in learning about a specific course, admission process, or campus facilities?",
            f"Can you rephrase your question? I'm here to help with topics like admissions, academic programs, campus life, and college facilities."
        ]
        return random.choice(clarifications)

    def _is_greeting(self, query):
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'greetings']
        return any(g in query.lower() for g in greetings)

    def _handle_greeting(self):
        responses = [
            "Hello! I'm TKRCET College Assistant. How can I help you today? Feel free to ask about admissions, courses, facilities, or anything about our college.",
            "Hi! Welcome to TKRCET College Assistant. What would you like to know about our college?",
            "Hey! I'm here to help with any questions about TKRCET College."
        ]
        return random.choice(responses)

    def _expand_abbreviations(self, query):
        """Expand common abbreviations to improve semantic matching"""
        abbreviations = {
            r'\bhod\b': 'head of department head department HOD',
            r'\bheads\b': 'head of department head department',
            r'\bdept\b': 'department',
            r'\bcs\b': 'computer science',
            r'\bcse\b': 'computer science and engineering cse head CSE department',
            r'\bcsm\b': 'CSE AIML artificial intelligence machine learning CSM department head',
            r'\bcsd\b': 'CSE DS data science CSD department head',
            r'\bece\b': 'electronics and communication engineering ece head ECE department',
            r'\beee\b': 'electrical and electronics engineering eee head EEE department',
            r'\bit\b': 'information technology it head IT department',
            r'\bmech\b': 'mechanical engineering mech head MECH department',
            r'\bce\b': 'civil engineering ce head CE department',
            r'\bba\b': 'bachelor of arts',
            r'\bma\b': 'master of arts',
            r'\btech\b': 'bachelor of technology',
            r'\bmtech\b': 'master of technology',
            r'\bphd\b': 'doctor of philosophy',
            r'\bsgpa\b': 'semester grade point average',
            r'\bcgpa\b': 'cumulative grade point average',
            r'\bfees\b': 'fee',
            r'\bprof\b': 'professor faculty Dr.',
            r'\bdr\b': 'doctor professor Dr.',
            r'\binfo\b': 'information',
            r'\bpls\b': 'please',
            r'\bupdates\b': 'update',
            r'\btiming\b': 'timings schedule',
            r'\bprincipal\b': 'principal director Dr.',
            r'\brector\b': 'rector principal director',
        }
        
        expanded_query = query.lower()
        for abbrev, expansion in abbreviations.items():
            expanded_query = re.sub(abbrev, expansion, expanded_query, flags=re.IGNORECASE)
        
        return expanded_query

    def _expand_query_with_gemma(self, query):
        """Use Gemma to expand query for better retrieval (optional, for multi-query)"""
        # This would call Gemma to generate query variants
        # For now, we'll use the abbreviation expansion + basic variants
        variants = [self._expand_abbreviations(query)]
        
        # Add basic semantic variants
        query_lower = query.lower()
        if 'who is' in query_lower or 'who are' in query_lower:
            variants.append(query.replace('who is', 'tell me about').replace('who are', 'tell me about'))
        
        if 'how to' in query_lower:
            variants.append(query.replace('how to', 'process of').replace('how to', 'procedure for'))
        
        return variants

    def _build_context_prompt(self, query, documents, history_context=""):
        """Build a relaxed, helpful prompt with conversation history"""
        # Import the prompt construction module
        from .prompt_construction import build_context_prompt, build_person_query_prompt
        
        # Check if this is a person query
        person_keywords = ['who', 'hod', 'principal', 'director', 'dean', 'registrar', 'founder', 'head', 'staff', 'teacher', 'professor']
        is_person_query = any(kw in query.lower() for kw in person_keywords)
        
        if is_person_query:
            prompt = build_person_query_prompt(query, documents, history_context)
        else:
            prompt = build_context_prompt(query, documents, history_context)
        
        return prompt 
        
    def _get_history_context(self):
        """Format recent conversation for context"""
        if not self.conversation_history:
            return ""
        
        history = []
        for i, (q, a) in enumerate(list(self.conversation_history)[-2:], 1):
            truncated_a = a[:100] + "..." if len(a) > 100 else a
            history.append(f"{i}. Q: {q}\n   A: {truncated_a}")
        return "\n".join(history)

    def search(self, query, k=5):
        """Hybrid search: Semantic (FAISS) + Keyword (BM25) retrieval with person boosting"""
        expanded_query = self._expand_abbreviations(query)
        query_variants = self._expand_query_with_gemma(query)
        
        # Boost retrieval for person-related queries
        person_keywords = ['who', 'principal', 'director', 'hod', 'dean', 'registrar', 'founder', 'name', 'head', 'prof', 'professor', 'dr', 'madam', 'sir']
        is_person_query = any(kw in query.lower() for kw in person_keywords)
        
        # Removed hardcoded HOD names - now relying on scraped data for accurate information
        
        if is_person_query:
            k = min(k + 15, len(self.chunks))  # Retrieve many more documents for person queries
        
        # ===== SEMANTIC SEARCH (FAISS) =====
        semantic_results = {}
        query_emb = self.embedding_model.encode(expanded_query, convert_to_tensor=True).cpu().detach().numpy().astype(np.float32)
        query_array = np.array([query_emb], dtype=np.float32)
        distances, indices = self.index.search(query_array, min(k, len(self.chunks)))  # type: ignore
        
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                doc = self.chunks[idx]
                text = doc.get('text', '').strip()
                
                # Skip navigation/menu-only text more aggressively
                if 'About Vision' in text and 'Organogram' in text:
                    continue  # Skip these menu navigation texts
                
                # For person queries, prioritize documents with "Dr." or actual names
                priority_boost = 0
                if is_person_query:
                    # Strong boost for actual person information
                    if 'Dr.' in text or 'Prof.' in text:
                        priority_boost += 2.0  # Big boost for Dr./Prof. titles
                    if 'Head' in text and 'Department' in text:
                        priority_boost += 1.5  # Boost for HOD mentions
                    if 'Principal' in text and len(text) > 100:
                        priority_boost += 1.5  # Boost for substantial principal info
                    if 'Dean' in text or 'Vice Principal' in text:
                        priority_boost += 1.0
                    # Penalize generic/irrelevant content
                    if 'emergency' in text.lower() or ('contact' in text.lower() and len(text) < 100):
                        priority_boost = -2.0  # Heavy penalty for generic contact lines
                    if text.count('|') > 3:  # Likely a table/list without context
                        priority_boost -= 0.5
                
                # Normalize distance to similarity score (0-1)
                semantic_results[idx] = {
                    'doc': doc,
                    'semantic_score': float(1 / (1 + distances[0][i])) + priority_boost,  # Add priority boost
                    'rank': i + 1
                }
        
        # Also retrieve from variants for improved coverage
        for variant in query_variants[1:]:
            variant_emb = self.embedding_model.encode(variant, convert_to_tensor=True).cpu().detach().numpy().astype(np.float32)
            variant_array = np.array([variant_emb], dtype=np.float32)
            v_distances, v_indices = self.index.search(variant_array, min(k, len(self.chunks)))  # type: ignore
            for i, idx in enumerate(v_indices[0]):
                if idx < len(self.chunks) and idx not in semantic_results:
                    doc = self.chunks[idx]
                    text = doc.get('text', '').strip()
                    
                    # Skip navigation/menu-only text
                    if 'About Vision' in text and 'Organogram' in text:
                        continue
                    
                    # Priority boost for person queries
                    priority_boost = 0
                    if is_person_query:
                        if 'Dr.' in text or 'Prof.' in text or 'Principal' in text:
                            priority_boost = 1.0
                        if 'emergency' in text.lower() or 'contact' in text.lower():
                            priority_boost = -0.5
                    
                    semantic_results[idx] = {
                        'doc': doc,
                        'semantic_score': float(1 / (1 + v_distances[0][i])) + priority_boost,
                        'rank': len(semantic_results) + 1
                    }
        
        # ===== KEYWORD SEARCH (BM25) =====
        tokenized_query = expanded_query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        keyword_results = {}
        for idx, score in enumerate(bm25_scores):
            if score > 0:  # Only include if there's a match
                doc = self.chunks[idx]
                text = doc.get('text', '').strip()
                
                # Skip navigation/menu-only text
                if 'About Vision' in text and 'Organogram' in text:
                    continue
                
                # Boost BM25 score for person-relevant content
                boosted_score = score
                if is_person_query and ('Dr.' in text or 'Prof.' in text):
                    boosted_score = score * 2.0  # Double boost for Dr./Prof. content
                
                if idx in semantic_results:
                    semantic_results[idx]['keyword_score'] = float(boosted_score)
                else:
                    keyword_results[idx] = {
                        'doc': doc,
                        'keyword_score': float(boosted_score),
                        'semantic_score': 0.0
                    }
        
        # ===== HYBRID RANKING (Combine both scores) =====
        combined_results = {}
        
        # Merge results
        all_results = {**semantic_results, **keyword_results}
        
        for idx, result in all_results.items():
            semantic_score = result.get('semantic_score', 0.0)
            keyword_score = result.get('keyword_score', 0.0)
            
            # Normalize keyword score (BM25 can have large values)
            normalized_keyword = min(keyword_score / 10.0, 1.0)  # Cap at 1.0
            
            # Hybrid score: weighted average (60% semantic, 40% keyword)
            hybrid_score = (0.6 * semantic_score) + (0.4 * normalized_keyword)
            
            combined_results[idx] = {
                'doc': result['doc'],
                'semantic_score': semantic_score,
                'keyword_score': keyword_score,
                'hybrid_score': hybrid_score
            }
        
        # Sort by hybrid score and return top k
        sorted_results = sorted(combined_results.items(), key=lambda x: x[1]['hybrid_score'], reverse=True)
        return [result['doc'] for idx, result in sorted_results[:k]]

    def rerank(self, query, documents, top_k=3):
        """Rerank documents by relevance"""
        if not documents:
            return []
        scores = self.cross_encoder.predict([(query, doc['text']) for doc in documents])
        ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return [doc for score, doc in ranked[:top_k]]

    def _generate_response(self, prompt, max_tokens=600, documents=None):
        """Generate response from Ollama or fallback to chain-based generator"""
        # If Ollama not available and we have fallback, use it
        if not self.ollama_available and self.chain_responder and documents:
            query = prompt.split("Question:")[-1].strip().split("\n")[0] if "Question:" in prompt else "Query"
            return self.chain_responder.respond(query, documents)
        
        if not self.ollama_available:
            if not documents:
                return "I couldn't find information to answer that. Please try a different question."
            # If no chain responder, just use documents as bullet points
            response = "Based on available information:\n\n"
            for doc in documents[:3]:
                response += f"• {doc.get('text', 'No text')[:200]}\n"
            return response.strip()
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.9, "num_predict": 800}  # Increased tokens and temperature
                },
                timeout=180  # Increased timeout for reliable generation
            )
            if response.status_code == 200:
                answer = response.json()['response'].strip()
                
                # Remove common truncation artifacts
                answer = answer.replace('thereby de', '').replace('thereby', '')
                
                # Clean up incomplete sentences
                if answer and not answer.endswith(('.', '?', '!', '•')):
                    # Find last sentence ending
                    for punct in ['.', '!', '?']:
                        last_idx = answer.rfind(punct)
                        if last_idx > 0 and last_idx > len(answer) * 0.4:
                            answer = answer[:last_idx + 1].strip()
                            break
                    
                    # If still no proper ending, keep it as is but mark it
                    if answer and not answer.endswith(('.', '?', '!')):
                        if len(answer) > 20:
                            answer = answer[:answer.rfind(' ')] if ' ' in answer else answer
                
                # Remove any remaining garbage/corrupted text
                lines = answer.split('\n')
                cleaned_lines = []
                for line in lines:
                    if len(line.strip()) > 3:  # Skip very short lines (likely garbage)
                        cleaned_lines.append(line)
                answer = '\n'.join(cleaned_lines).strip()
                
                return answer if answer else "I could not generate a proper response. Please try again."
            return f"Error: Ollama returned status {response.status_code}"
        except requests.exceptions.Timeout:
            # Fallback to chain responder on timeout
            if self.chain_responder and documents:
                query = prompt.split("Question:")[-1].strip().split("\n")[0] if "Question:" in prompt else "Query"
                return self.chain_responder.respond(query, documents)
            return "Error: Response generation timed out. Please try again."
        except requests.exceptions.ConnectionError:
            # Use fallback on connection error
            if self.chain_responder and documents:
                query = prompt.split("Question:")[-1].strip().split("\n")[0] if "Question:" in prompt else "Query"
                return self.chain_responder.respond(query, documents)
            return "Error: Cannot connect to Ollama. Please ensure it's running."
        except Exception as e:
            return f"Error: {str(e)}"

    def __call__(self, query):
        """Main RAG pipeline with context awareness"""
        query = query.strip()
        if not query:
            return "Please enter a question."
        
        # Handle greetings
        if self._is_greeting(query):
            response = self._handle_greeting()
        # Detect unclear queries
        elif not self._is_query_clear(query):
            response = self._ask_clarification(query)
        else:
            # Full RAG pipeline with history
            history_context = self._get_history_context()
            retrieved = self.search(query, k=5)
            reranked = self.rerank(query, retrieved, top_k=3)
            prompt = self._build_context_prompt(query, reranked, history_context)
            response = self._generate_response(prompt, max_tokens=800, documents=reranked)  # Increased from 500 to 800
        
        # Store in history
        self.conversation_history.append((query, response))
        return response


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("RAG SYSTEM TEST")
    print("=" * 70 + "\n")
    
    rag = RAGSystem()
    
    test_queries = [
        "What is the admission process?",
        "Tell me about college facilities",
        "What courses are offered?",
        "hi",
        "blah"
    ]
    
    for query in test_queries:
        print(f"Q: {query}")
        answer = rag(query)
        print(f"A: {answer}\n")
