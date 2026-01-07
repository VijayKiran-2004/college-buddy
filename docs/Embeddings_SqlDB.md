##  Data Storage & Embedding Strategy

###  Student Dataset — Stored in SQL Database
The student dataset contains **structured and critical academic records** such as Roll Number, Name, CGPA, Credits, Results, and Placement details.  
This data is stored in an **SQL database (`students.db`)

** because:
- SQL is ideal for **structured relational data**
- Ensures **100% accuracy** (prevents hallucinations)
- Supports **fast indexed queries**
- Maintains **data consistency & constraints**
- Industry-standard method for handling academic records

SQL is used for deterministic queries like:
- Student details
- CGPA / Credits
- Result status
- Placement information



###  FAQ Dataset — Embedded for Semantic Retrieval
The FAQ dataset consists of **question–answer pairs** and is converted into embeddings to enable **semantic search** instead of simple text matching.

#### **Embedding Model Used**
`BAAI/bge-large-en-v1.5`

#### **Embedding Technique**
- Built using **Sentence Transformers**
- Generates **dense vector embeddings**
- Embeddings are **normalized** for stable cosine similarity
- Designed specifically for **Retrieval-Augmented Generation (RAG)** systems
- Enables understanding of paraphrased questions and user intent

This allows retrieving the correct FAQ even when the user phrases the question differently.



###  Web-Scraped College Data — Embedded for Knowledge Retrieval
The web-scraped college content contains **long unstructured informational content** such as college overview, departments, facilities, and accreditation information.

The same embedding approach is used here.

#### **Embedding Model Used**
`BAAI/bge-large-en-v1.5`

#### **Embedding Technique**
- Web content is chunked into readable segments
- Each chunk is converted into **semantic vector embeddings**
- Stored for similarity-based retrieval
- Enables deep contextual understanding

Using the **same embedding model** for both FAQ and Web data ensures:
- Both datasets exist in the **same vector space**
- Uniform similarity scoring
- Highly accurate retrieval results



###  Final Summary
Student Dataset - SQL Database - Structured, accuracy required 
FAQ Dataset - Vector Embeddings - Semantic question answering 
Web Data - Vector Embeddings - Contextual knowledge retrieval 
