import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama


# ==================================================
# PROMPT CONSTRUCTION (FINAL, AUTHORITATIVE)
# ==================================================
def construct_prompt(user_query, rag_system, user_role="student"):
    """
    Builds the final prompt using the RAG system and strict rules.
    Assumes RAG search + rerank are already implemented and correct.
    """

    # --- Retrieve context via RAG ---
    retrieved_docs = rag_system.search(user_query, k=5)
    reranked_docs = rag_system.rerank(user_query, retrieved_docs)

    if not reranked_docs:
        context_text = "No relevant college information found."
    else:
        context_text = "\n".join(f"- {doc['text']}" for doc in reranked_docs)

    # --- System instructions ---
    system_instructions = """
You are an AI-powered College Assistant Chatbot.

ROLE:
- Assist only with college-related queries.
- Be polite, professional, and concise.

STRICT RULES:
1. Answer ONLY college-related questions.
2. Use ONLY the retrieved knowledge base below.
3. Do NOT guess or hallucinate.
4. If the answer is missing, say:
   "This information is currently not available in the system. Please contact the college admin department for accurate details."
5. For greetings, respond politely and ask how you can help.
6. Mention relevant college portals when applicable.
"""

    # --- Final prompt ---
    final_prompt = f"""
{system_instructions}

RETRIEVED KNOWLEDGE BASE:
{context_text}

USER ROLE:
{user_role}

USER QUERY:
{user_query}

FINAL ANSWER:
"""

    return final_prompt.strip()


# ==================================================
# LLM IMPLEMENTATION (CLEAN & SAFE)
# ==================================================
class CollegeBotLLM:
    def __init__(self):
        # Download small, stable GGUF model (CPU-safe)
        model_path = hf_hub_download(
            repo_id="microsoft/Phi-3-mini-4k-instruct-gguf",
            filename="Phi-3-mini-4k-instruct-q4.gguf"
        )

        # Initialize LLM
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )

    def generate_response(self, user_query, rag_system, user_role="student"):
        """
        Complete LLM responsibility:
        - Prompt construction
        - Decoding
        - Response generation
        """

        prompt = construct_prompt(
            user_query=user_query,
            rag_system=rag_system,
            user_role=user_role
        )

        output = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            stop=["USER QUERY:", "RETRIEVED KNOWLEDGE BASE:"]
        )

        return output["choices"][0]["text"].strip()


# ==================================================
# MINIMAL TEST (WILL RUN WITHOUT ERRORS)
# ==================================================
if __name__ == "__main__":

    # Dummy RAG for validation (replace with your real RAG)
    class DummyRAG:
        def search(self, query, k=5):
            return [
                {"text": "The Head of the Computer Science department is Dr. Smith."},
                {"text": "CS department office hours are from 10 AM to 12 PM."}
            ]

        def rerank(self, query, docs):
            return docs

    rag_system = DummyRAG()
    bot = CollegeBotLLM()

    query = "Who is the HOD of CS and when can I meet him?"
    response = bot.generate_response(query, rag_system)

    print("\nBot Response:\n")
    print(response)