# AI Powered Conversational Chatbot for College Website Navigation and Student Assistance
## Overview

This project is a College Chatbot designed to answer queries related to college information such as departments, faculty, students, placements, and FAQs.
It uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses based on stored college data.

## Key Features

College information Q&A

Student & faculty data retrieval

Placement-related queries

Semantic search using embeddings

Modular and scalable project structure

## Tech Stack

**Programming Language :** Python

**Backend:** FastAPI 

**Vector Database:** ChromaDB

**Embeddings:** Sentence Transformers - BAAI/bge-large-en-v1.5

**LLM:** Gemma 3N E2B

## Project Structure  
college-chatbot/  
│  
├── app/              # Core backend logic  
├── data/             # Datasets, embeddings, chunks  
├── scripts/          # Utility & processing scripts  
├── docs/             # Detailed documentation  
├── static/           # Frontend / UI files   
│  
├── requirements.txt  
├── README.md  
└── .gitignore  

## Setup Instructions
1️⃣ Clone the repository  
git clone https://github.com/sanjana861/college-chatbot.git  
cd college-chatbot  

2️⃣ Create virtual environment  
python -m venv venv  
source venv/bin/activate   # Windows: venv\Scripts\activate  

3️⃣ Install dependencies  
pip install -r requirements.txt

4️⃣ Run the application  
python app/main.py

## Data Handling

Raw scraped data → data/scraped_data/

Cleaned datasets → data/datasets/

Text chunks → data/chunks/

Vector embeddings → data/embeddings/

## Team Roles & Responsibilities

**Sanjana**           : Chunking & Tokenization  
**Subhash Chandra**   : Embeddings & SQL Database  
**Sathish**           : Vector Database  
**Vijay Kiran**       : Retrieval-Augmented Generation (RAG)  
**Mokshagna**         : LLM Integration  
**Vishnuvardhan**     : Prompt Construction  
**Praneetha**         : Fine-Tuning  


## Documentation

Detailed documentation is available in the docs/ folder:

chunking.md – Chunking details

embeddings.md – Embeddings details

rag.md – Rag Wrokflow


## Notes

Do not push venv/ or .env files

Use branches for team collaboration

Create pull requests for merging

## License

This project is developed for academic purposes.
