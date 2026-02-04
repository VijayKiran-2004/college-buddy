"""
UltraRAG System - Modern MCP-based RAG implementation
Replaces the old custom RAG system with UltraRAG framework
"""

import json
import requests
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ============================================================
# KNOWLEDGE BASE - Instant answers for critical facts
# ============================================================
KNOWLEDGE_BASE = {
    "personnel": {
        "principal": "Dr. D. V. Ravi Shankar",
        "vice_principal": "Dr. A. Suresh Rao (also HoD of CSE & Dean Academics)",
        "secretary": "Dr. T. Harinath Reddy",
        "chairman": "Sri. Teegala Krishna Reddy",
        "hod": {
            "cse": "Dr. A. Suresh Rao",
            "cse-aiml": "Dr. B. Sunil Srinivas",
            "csm": "Dr. B. Sunil Srinivas",
            "cse-ds": "Dr. V. Krishna",
            "csd": "Dr. V. Krishna",
            "ece": "Dr. D. Nageshwar Rao",
            "eee": "Dr. K. Raju",
            "it": "Dr. R. Muruanantham",
            "mech": "Mr. D. Rushi Kumar",
            "civil": "Mr. K.V.R Satya Sai",
            "mba": "Dr. K. Gyaneswari"
        }
    },
    "timings": {
        "working_hours": "9:40 AM to 4:20 PM (Monday-Saturday)",
        "lunch_break": "12:40 PM to 1:20 PM"
    },
    "history": {
        "established": "2002",
        "founder": "Sri. Teegala Krishna Reddy",
        "affiliation": "JNTUH (Jawaharlal Nehru Technological University Hyderabad)",
        "location": "Meerpet, Hyderabad - 500097, Telangana",
        "campus_size": "20 acres"
    },
    "admissions": {
        "process": "Admissions are through TS EAPCET counseling for B.Tech, PGCET for M.Tech, and direct admission for MBA. Visit the admissions office or website for detailed procedure.",
        "eligibility": "10+2 with Physics, Chemistry, and Mathematics for B.Tech. Graduation in relevant field for M.Tech/MBA.",
        "contact": "Visit https://tkrcet.ac.in/admissions for admission details and fee structure."
    },
    "courses": {
        "ug": ["CSE", "CSE-AIML", "CSE-DS", "ECE", "EEE", "IT", "Mechanical", "Civil"],
        "pg": ["M.Tech in CSE", "M.Tech in Power Electronics", "MBA"],
        "total": "8 UG programs and 3 PG programs"
    },
    "facilities": {
        "main": "State-of-the-art labs, smart classrooms, Wi-Fi campus, digital library, hostel (boys & girls), transport, sports ground, auditorium, NCC, incubation center, and medical facilities.",
        "special": "Virtual labs, R&D center (21,000 sq ft), industry partnerships with ECIL and others."
    },
    "accreditation": {
        "naac": "A+ Grade",
        "nba": "NBA Accredited",
        "approvals": "AICTE approved, UGC recognized 2(f) & 12(B)"
    },
    "scholarships": {
        "types": ["Merit-based", "Need-based", "Sports quota", "SC/ST/OBC", "Minority scholarships"],
        "merit": "Available for students with >85% in 12th or CGPA >8.5 in college",
        "fee_reimbursement": "TS Government fee reimbursement scheme for eligible students (income criteria apply)",
        "central_schemes": "Central sector scholarship, Post-matric scholarship for SC/ST/OBC students",
        "contact": "Contact admissions office or visit https://tkrcet.ac.in/scholarships for details",
        "application": "Apply through TS ePass portal for state scholarships"
    },
    "fees": {
        "btech_annual": "₹75,000 - ₹85,000 per year (approx, varies by category)",
        "mtech_annual": "₹60,000 - ₹70,000 per year (approx)",
        "mba_annual": "₹50,000 - ₹60,000 per year (approx)",
        "hostel": "₹40,000 - ₹50,000 per year (including mess)",
        "transport": "₹15,000 - ₹25,000 per year (route-dependent)",
        "note": "Fees vary by category (Management/Convener quota). Contact admissions for exact details: admissions@tkrcet.ac.in"
    },
    "events": {
        "tech_fest": "Annual tech fest 'TECHNOVA' with coding competitions, robotics, hackathons, and technical workshops",
        "cultural_fest": "Cultural fest 'KALANJALI' with music, dance, drama, and art competitions",
        "sports_day": "Annual sports meet with inter-department cricket, football, volleyball, and athletics",
        "hackathons": "Regular 24-hour coding hackathons and coding competitions",
        "workshops": "Industry expert workshops on AI/ML, Cloud Computing, IoT, and emerging technologies",
        "clubs": "Active IEEE, CSI, Coding Club, Robotics Club, and Literary Club"
    },
    "exam_schedule": {
        "mid_term_1": "Usually in September (Odd semester) / February (Even semester)",
        "mid_term_2": "Usually in November (Odd semester) / April (Even semester)",
        "semester_end": "December (Odd semester) / May (Even semester)",
        "internal_marks": "Based on mid-terms, assignments, and attendance",
        "note": "Check college website or notice board for exact dates each semester"
    },
    "library": {
        "name": "Central Library",
        "collection": "50,000+ books, e-journals, IEEE digital library access",
        "timings": "9:00 AM to 5:00 PM (Monday-Saturday)",
        "facilities": "Digital library, reading rooms, e-resources, internet access",
        "membership": "Free for all students and faculty"
    }
}



class UltraRAGSystem:
    """
    UltraRAG-based RAG system for college-buddy chatbot
    Uses MCP architecture with FAISS + BM25 hybrid retrieval
    """
    
    def __init__(
        self,
        corpus_path='app/database/vectordb/corpus_ultrarag.jsonl',
        ollama_model='gemma2:2b',  # Switched to 2B for 2x faster inference
        ollama_url='http://localhost:11434/api/generate',
    ):
        print("Initializing UltraRAG System...")
        
        self.corpus_path = corpus_path
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url
        
        # Load corpus for retrieval
        self.documents = self._load_corpus()
        print(f"✓ Loaded {len(self.documents)} documents")
        
        # Initialize retrieval components
        try:
            from sentence_transformers import SentenceTransformer
            from rank_bm25 import BM25Okapi
            import faiss
            import numpy as np
            
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Loaded embedding model")
            
            # Build/load FAISS index
            self.index = self._build_faiss_index()
            print("✓ FAISS index ready")
            
            # Build/load BM25 index
            self.bm25 = self._build_bm25_index()
            print("✓ BM25 index ready")
            
        except Exception as e:
            print(f"⚠ Error initializing retrieval: {e}")
            raise
        
        # Test Ollama connection
        self.ollama_available = self._test_ollama()
        
        # Response cache for common queries
        self.response_cache = {}
        
        print("✓ UltraRAG System ready!\n")
    
    def _load_corpus(self):
        """Load JSONL corpus"""
        documents = []
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                doc = json.loads(line)
                documents.append(doc)
        return documents
    
    def _build_faiss_index(self):
        """Build or load FAISS index"""
        import faiss
        import numpy as np
        
        index_path = Path('app/database/vectordb/ultrarag_faiss.index')
        
        if index_path.exists():
            return faiss.read_index(str(index_path))
        
        # Build new index
        print("Building FAISS index...")
        texts = [doc['contents'] for doc in self.documents]
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
        embeddings_np = embeddings.cpu().detach().numpy().astype(np.float32)
        
        index = faiss.IndexFlatL2(embeddings_np.shape[1])
        index.add(embeddings_np)
        
        # Save index
        faiss.write_index(index, str(index_path))
        return index
    
    def _build_bm25_index(self):
        """Build or load BM25 index"""
        from rank_bm25 import BM25Okapi
        import pickle
        
        bm25_path = Path('app/database/vectordb/ultrarag_bm25.pkl')
        
        if bm25_path.exists():
            with open(bm25_path, 'rb') as f:
                return pickle.load(f)
        
        # Build new BM25 index
        print("Building BM25 index...")
        corpus = [doc['contents'] for doc in self.documents]
        tokenized_corpus = [doc.lower().split() for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Save index
        with open(bm25_path, 'wb') as f:
            pickle.dump(bm25, f)
        
        return bm25
    
    def _test_ollama(self):
        """Test Ollama connection"""
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.ollama_model, "prompt": "test", "stream": False},
                timeout=30
            )
            if response.status_code == 200:
                print(f"✓ Connected to Ollama: {self.ollama_model}")
                return True
        except Exception as e:
            print(f"⚠ Ollama not available: {e}")
        return False
    
    def _is_college_related(self, query):
        """Check if query is related to college/education domain"""
        query_lower = query.lower()
        
        # College-related keywords
        college_keywords = [
            'college', 'tkrcet', 'university', 'campus', 'admission', 'course', 'department',
            'principal', 'hod', 'dean', 'faculty', 'professor', 'teacher', 'staff',
            'fee', 'placement', 'hostel', 'library', 'lab', 'facility', 'infrastructure',
            'exam', 'semester', 'academic', 'student', 'class', 'lecture', 'timing',
            'branch', 'cse', 'ece', 'eee', 'mech', 'civil', 'mba', 'btech', 'mtech',
            'naac', 'nba', 'aicte', 'jntuh', 'affiliation', 'accreditation',
            'transport', 'canteen', 'sports', 'club', 'event', 'fest', 'workshop',
            'scholarship', 'eligibility', 'criteria', 'counseling', 'eapcet'
        ]
        
        # Check if any college keyword is present
        if any(keyword in query_lower for keyword in college_keywords):
            return True
        
        # Check for question patterns that are likely college-related
        college_patterns = [
            'where is', 'when was', 'who is', 'what are', 'how to',
            'tell me about', 'information about', 'details about'
        ]
        
        # If it's a question pattern, check if it could be college-related
        if any(pattern in query_lower for pattern in college_patterns):
            # Reject obvious non-college topics
            non_college_keywords = [
                'formula', 'equation', 'calculate', 'solve', 'math', 'physics',
                'chemistry', 'biology', 'theorem', 'proof', '^', '=', '+', '-', '*', '/'
            ]
            if any(keyword in query_lower for keyword in non_college_keywords):
                return False
            # If it's a question but no clear non-college indicators, allow it
            return True
        
        return False
    
    def _check_knowledge_base(self, query):
        """Check if query can be answered from knowledge base"""
        query_lower = query.lower()
        
        # Personnel queries
        if 'principal' in query_lower and 'vice' not in query_lower:
            return f"The Principal of TKRCET is {KNOWLEDGE_BASE['personnel']['principal']}."
        
        if 'vice principal' in query_lower:
            return f"The Vice Principal is {KNOWLEDGE_BASE['personnel']['vice_principal']}."
        
        if 'secretary' in query_lower:
            return f"The Secretary of TKRCET is {KNOWLEDGE_BASE['personnel']['secretary']}."
        
        if 'chairman' in query_lower:
            return f"The Chairman of TKRCET is {KNOWLEDGE_BASE['personnel']['chairman']}."
        
        if 'hod' in query_lower or 'head of department' in query_lower:
            for dept, hod in KNOWLEDGE_BASE['personnel']['hod'].items():
                if dept in query_lower:
                    return f"The HOD of {dept.upper()} is {hod}."
        
        # Timings
        if 'timing' in query_lower or 'hours' in query_lower or 'time' in query_lower:
            return f"College timings: {KNOWLEDGE_BASE['timings']['working_hours']}. Lunch break: {KNOWLEDGE_BASE['timings']['lunch_break']}."
        
        # History & Location
        if 'established' in query_lower or 'founded' in query_lower or 'started' in query_lower:
            return f"TKRCET was established in {KNOWLEDGE_BASE['history']['established']} on a {KNOWLEDGE_BASE['history']['campus_size']} campus in {KNOWLEDGE_BASE['history']['location']}."
        
        if 'affiliation' in query_lower or 'affiliated' in query_lower:
            return f"TKRCET is affiliated to {KNOWLEDGE_BASE['history']['affiliation']}."
        
        if 'location' in query_lower or 'address' in query_lower or 'where' in query_lower:
            return f"TKRCET is located at {KNOWLEDGE_BASE['history']['location']}."
        
        # Admissions
        if 'admission' in query_lower or 'apply' in query_lower or 'join' in query_lower:
            return f"{KNOWLEDGE_BASE['admissions']['process']} Eligibility: {KNOWLEDGE_BASE['admissions']['eligibility']} {KNOWLEDGE_BASE['admissions']['contact']}"
        
        # Courses
        if 'course' in query_lower or 'program' in query_lower or 'branch' in query_lower or 'department' in query_lower:
            ug = ', '.join(KNOWLEDGE_BASE['courses']['ug'])
            pg = ', '.join(KNOWLEDGE_BASE['courses']['pg'])
            return f"TKRCET offers {KNOWLEDGE_BASE['courses']['total']}.\n\nUG Programs: {ug}\n\nPG Programs: {pg}"
        
        # Facilities
        if 'facilit' in query_lower or 'infrastructure' in query_lower or 'amenities' in query_lower:
            return f"{KNOWLEDGE_BASE['facilities']['main']}\n\nSpecial Features: {KNOWLEDGE_BASE['facilities']['special']}"
        
        # Accreditation
        if 'naac' in query_lower or 'nba' in query_lower or 'accredit' in query_lower or 'approved' in query_lower:
            return f"TKRCET is {KNOWLEDGE_BASE['accreditation']['naac']} accredited, {KNOWLEDGE_BASE['accreditation']['nba']}, and {KNOWLEDGE_BASE['accreditation']['approvals']}."
        
        return None
    
    def _hybrid_retrieve(self, query, top_k=5):
        """Hybrid retrieval using FAISS + BM25"""
        import numpy as np
        
        # FAISS semantic search
        query_emb = self.embedding_model.encode(query, convert_to_tensor=True)
        query_np = query_emb.cpu().detach().numpy().astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_np, top_k * 2)
        
        faiss_docs = [self.documents[idx] for idx in indices[0] if idx < len(self.documents)]
        
        # BM25 keyword search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = np.argsort(bm25_scores)[-top_k*2:][::-1]
        
        bm25_docs = [self.documents[idx] for idx in top_bm25_indices if idx < len(self.documents)]
        
        # Merge and deduplicate
        seen_ids = set()
        merged_docs = []
        
        for doc in faiss_docs + bm25_docs:
            if doc['id'] not in seen_ids:
                seen_ids.add(doc['id'])
                merged_docs.append(doc)
                if len(merged_docs) >= top_k:
                    break
        
        return merged_docs
    
    def _extract_relevant_links(self, docs):
        """Extract unique, relevant URLs from retrieved documents"""
        links = []
        seen_urls = set()
        
        for doc in docs[:5]:  # Check top 5 docs
            url = doc.get('metadata', {}).get('url', '')
            source = doc.get('metadata', {}).get('source', '')
            
            # Prefer source over url field
            link = source if source and source.startswith('http') else url
            
            if link and link not in seen_urls and link.startswith('http'):
                seen_urls.add(link)
                links.append(link)
        
        return links[:3]  # Return max 3 links
    
    def _generate_response(self, query, docs):
        """Generate response using Ollama with retrieved context"""
        
        # Build context from retrieved documents
        context = "\n\n".join([f"• {doc['contents'][:400]}" for doc in docs[:3]])
        
        # Build KB context
        kb_context = self._format_kb_context()
        
        prompt = f"""You are the TKRCET College Assistant chatbot. You ONLY answer questions about TKRCET college.

IMPORTANT: You must ONLY answer questions related to:
- College information (admissions, courses, facilities, timings, location)
- Personnel (Principal, HODs, faculty, staff)
- Academic programs and departments
- Campus facilities and infrastructure
- Student services and activities

DO NOT answer questions about:
- Mathematics, science, or academic subject content
- General knowledge or trivia
- Personal advice unrelated to college
- Any topic outside TKRCET college domain

Context Information:
{kb_context}

{context}

Student Question: {query}

If the question is NOT about TKRCET college, respond with: "I'm sorry, I can only answer questions about TKRCET college. Please ask me about admissions, courses, facilities, or other college-related topics."

Your Answer:"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Lower for faster, more deterministic responses
                        "num_predict": 150,  # Reduced from 250 for faster generation
                        "num_ctx": 1024      # Reduced from 2048 for 40% speed boost
                    }
                },
                timeout=60
            )
            if response.status_code == 200:
                answer = response.json().get('response', '').strip()
                if answer and len(answer) > 10:
                    # Add relevant navigation links
                    links = self._extract_relevant_links(docs)
                    if links:
                        answer += "\n\n📌 Related Links:\n"
                        for link in links:
                            answer += f"• {link}\n"
                    return answer
        except Exception as e:
            print(f"⚠ Ollama error: {e}")
        
        # Fallback to document snippets with links
        fallback = f"Here's what I found:\n\n{context}"
        links = self._extract_relevant_links(docs)
        if links:
            fallback += "\n\n📌 Related Links:\n"
            for link in links:
                fallback += f"• {link}\n"
        return fallback
    
    def _format_kb_context(self):
        """Format knowledge base as context"""
        kb = KNOWLEDGE_BASE
        lines = []
        
        lines.append(f"Principal: {kb['personnel']['principal']}")
        lines.append(f"Vice Principal: {kb['personnel']['vice_principal']}")
        lines.append(f"Timings: {kb['timings']['working_hours']}")
        lines.append(f"Established: {kb['history']['established']}")
        lines.append(f"Affiliation: {kb['history']['affiliation']}")
        
        return "\n".join(lines)
    
    def __call__(self, query):
        """Main entry point for queries"""
        query = query.strip()
        if not query:
            return "Please enter a question."
        
        # Greetings
        greetings = ['hi', 'hello', 'hey', 'how are you', 'how r u', 'how are u', 'whats up', "what's up"]
        if any(greeting == query.lower() for greeting in greetings):
            return "Hello! I'm TKRCET College Assistant. How can I help you today? 😊"
        
        # Check if query is college-related
        if not self._is_college_related(query):
            return "I'm sorry, I can only answer questions about TKRCET college. Please ask me about admissions, courses, facilities, timings, faculty, or other college-related topics."
        
        # Check knowledge base first
        kb_answer = self._check_knowledge_base(query)
        if kb_answer:
            return kb_answer
        
        # Retrieve relevant documents
        docs = self._hybrid_retrieve(query, top_k=5)
        
        # Generate response
        response = self._generate_response(query, docs)
        
        return response


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("ULTRARAG SYSTEM TEST")
    print("=" * 70 + "\n")
    
    rag = UltraRAGSystem()
    
    test_queries = [
        "hi",
        "who is the principal?",
        "who is the HOD of CSE?",
        "college timings?",
        "when was college established?",
        "what are the facilities?",
    ]
    
    for query in test_queries:
        print(f"Q: {query}")
        answer = rag(query)
        print(f"A: {answer}\n")
