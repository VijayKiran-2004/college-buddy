# College Chatbot RAG System

This document provides a detailed overview of the Retrieval-Augmented Generation (RAG) system implemented in this project. The goal of this system is to create a conversational AI that can answer user questions about a college accurately and contextually.

## Overview

In the domain of college-related inquiries, students, parents, and staff often have a wide range of questions, from admission procedures and fee structures to campus life and course details. A traditional chatbot might struggle to provide accurate and up-to-date information. This RAG system addresses this challenge by combining the power of a pre-trained language model with an external knowledge base.

The system is designed to be:
*   **Accurate:** By retrieving information from a curated knowledge base, the system can provide answers based on factual data.
*   **Contextual:** The system can understand the nuances of user queries and provide relevant answers.
*   **Extensible:** The knowledge base can be easily updated with new information, ensuring the chatbot stays current.

## RAG Pipeline

The RAG system follows a three-stage pipeline to generate answers:

### 1. Retrieval

The first stage is to find the most relevant information from the knowledge base. The knowledge base in this project is a collection of text chunks and FAQs stored in `app/database/vectordb/unified_vectors.json`.

*   **Embedding:** Although the `unified_vectors.json` file contains pre-computed embeddings, they were generated with a different model. To ensure consistency, the text data is loaded and the embeddings are re-generated in memory using the `all-MiniLM-L6-v2` sentence-transformer model upon initialization of the `RAGSystem`. These embeddings capture the semantic meaning of the text.
*   **Indexing:** The newly generated embeddings are stored in a FAISS index, which is a highly efficient library for similarity search.
*   **Searching:** When a user asks a question, the query is also embedded using the same `all-MiniLM-L6-v2` model. The FAISS index is then used to find the most similar document embeddings to the query embedding, using the L2 distance metric. This process is known as a dense vector search.

### 2. Reranking

The initial retrieval stage is optimized for speed and may not always return the most relevant documents at the top. The reranking stage refines the search results.

*   **Cross-Encoder:** A cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`) is used to get a more accurate relevance score. Unlike the sentence-transformer, which embeds the query and documents independently, the cross-encoder takes both the query and a document as input simultaneously, allowing it to better model their interaction.
*   **Sorting:** The documents are then sorted based on the scores from the cross-encoder, with the most relevant documents moving to the top.

### 3. Generation

The final stage is to generate a human-like answer based on the retrieved and reranked documents.

*   **Language Model:** A pre-trained T5 model (`google/flan-t5-base`) is used for this task. T5 (Text-to-Text Transfer Transformer) is a versatile model that can be fine-tuned for a variety of NLP tasks, including question answering.
*   **Contextual Answer:** The query and the top-ranked documents are combined into a prompt that is fed to the T5 model. The model then generates an answer based on the provided context.

## Decoding Strategy

To control the creativity and factuality of the generated answer, a hybrid decoding strategy is used:

*   **High Temperature (e.g., 0.7):** A temperature greater than 0 and less than 1 encourages the model to generate more diverse and less predictable text. This can make the answers sound more natural.
*   **Top-K Sampling (e.g., k=50):** This method restricts the model's vocabulary to the top `k` most likely next words. This helps to avoid generating nonsensical words.
*   **Top-P Sampling (e.g., p=0.9):** Also known as nucleus sampling, this method selects the next word from a vocabulary of the most probable words whose cumulative probability is greater than or equal to `p`. This is a more dynamic approach than top-k sampling and can lead to more creative answers.

By combining these three techniques, we can generate answers that are both creative and grounded in the retrieved context.

## Technologies Used

The RAG system is built using the following open-source libraries and models:

*   **`sentence-transformers`:** A Python framework for state-of-the-art sentence, text, and image embeddings.
    *   **`all-MiniLM-L6-v2`:** A fast and high-quality model for generating sentence embeddings.
    *   **`cross-encoder/ms-marco-MiniLM-L-6-v2`:** A cross-encoder model fine-tuned on the MS MARCO dataset, which is a large-scale dataset for machine reading comprehension.
*   **`faiss-cpu`:** A library developed by Facebook AI for efficient similarity search and clustering of dense vectors. The CPU version is used for broad compatibility.
*   **`transformers`:** A library by Hugging Face that provides thousands of pre-trained models for a wide range of NLP tasks.
    *   **`google/flan-t5-base`:** A T5 model that has been fine-tuned on a large collection of datasets, making it a powerful tool for a variety of NLP tasks.
*   **`torch`:** A popular open-source machine learning library.
*   **`accelerate`:** A library by Hugging Face that simplifies running PyTorch models on any kind of distributed setup.
*   **`numpy`:** A fundamental package for scientific computing with Python.
*   **`sentencepiece`:** A library for unsupervised text tokenization and detokenization.

## Code Structure (`app/services/rag_services.py`)

The entire RAG pipeline is encapsulated in the `RAGSystem` class in `app/services/rag_services.py`.

*   **`__init__(self, ...)`:**
    *   Loads the text chunks from the JSON file.
    *   Initializes the `SentenceTransformer` for embedding, the `CrossEncoder` for reranking, and the `T5Tokenizer` and `T5ForConditionalGeneration` for the generative part.
    *   Encodes all the text chunks and builds the FAISS index.
*   **`search(self, query, k=5)`:**
    *   Takes a user query as input.
    *   Encodes the query to a vector.
    *   Performs a similarity search on the FAISS index to retrieve the top `k` most similar documents.
*   **`rerank(self, query, documents)`:**
    *   Takes the user query and the retrieved documents as input.
    *   Uses the cross-encoder to calculate a relevance score for each query-document pair.
    *   Returns the documents sorted by their relevance scores.
*   **`generate(self, query, documents, ...)`:**
    *   Takes the user query and the reranked documents as input.
    *   Constructs a prompt by combining the query and the context from the documents.
    *   Uses the T5 model to generate an answer based on the prompt.
    *   The generation process is controlled by the `temperature`, `top_k`, and `top_p` parameters.
*   **`__call__(self, query)`:**
    *   The main entry point for the RAG system.
    *   It takes a user query and orchestrates the entire search-rerank-generate pipeline.
    *   Returns the final generated answer.

## How to Run

1.  **Set up the environment:**
    *   Create a virtual environment: `python -m venv venv`
    *   Activate the virtual environment: `venv\Scripts\activate`

2.  **Install dependencies:**
    *   Install all the required packages from `requirements.txt`: `pip install -r requirements.txt`

3.  **Run the RAG system:**
    *   Execute the `rag_services.py` script: `python app/services/rag_services.py`
