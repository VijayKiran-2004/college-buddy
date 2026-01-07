#!/usr/bin/env python3
"""
Terminal-based College Chatbot
Interactive RAG system using Ollama Gemma 3N E2B model
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_system import RAGSystem


class TerminalChatbot:
    """Interactive terminal chatbot interface"""
    
    def __init__(self):
        """Initialize chatbot with RAG system"""
        print("\n" + "=" * 70)
        print("COLLEGE CHATBOT - TERMINAL VERSION")
        print("=" * 70)
        print("Initializing chatbot system...")
        print()
        
        try:
            self.rag = RAGSystem()
            self.running = True
            print("\n✓ Chatbot initialized successfully!")
            print("=" * 70)
        except Exception as e:
            print(f"\n✗ Error initializing chatbot: {str(e)}")
            print("Make sure:")
            print("  1. All data files are present")
            print("  2. Ollama service is running: ollama run gemma3:1b")
            self.running = False

    def print_welcome(self):
        """Print welcome message"""
        print("\n" + "=" * 70)
        print("Welcome to TKRCET College Assistant Chatbot")
        print("=" * 70)
        print("\nYou can ask questions about:")
        print("  • Admission process and criteria")
        print("  • College facilities and infrastructure")
        print("  • Courses and academic programs")
        print("  • Contact information")
        print("  • Campus life and activities")
        print("\nType 'help' for available commands")
        print("Type 'exit' or 'quit' to exit")
        print("=" * 70 + "\n")

    def print_help(self):
        """Print help information"""
        print("\n" + "-" * 70)
        print("AVAILABLE COMMANDS:")
        print("-" * 70)
        print("  help          - Show this help message")
        print("  clear         - Clear screen")
        print("  status        - Show system status")
        print("  exit / quit   - Exit the chatbot")
        print("-" * 70)
        print("\nJust type your question and press Enter to get an answer!")
        print("-" * 70 + "\n")

    def print_status(self):
        """Print system status"""
        print("\n" + "-" * 70)
        print("SYSTEM STATUS")
        print("-" * 70)
        try:
            num_chunks = len(self.rag.chunks)
            print(f"✓ Knowledge Base: {num_chunks} chunks loaded")
            print(f"✓ Embedding Model: all-MiniLM-L6-v2")
            print(f"✓ LLM Model: Gemma 3 1B (via Ollama)")
            print(f"✓ Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2")
            print(f"✓ Conversation History: {len(self.rag.conversation_history)} messages")
            print("-" * 70 + "\n")
        except Exception as e:
            print(f"✗ Error getting status: {str(e)}\n")

    def format_answer(self, answer):
        """Format answer for display (no truncation)"""
        if not answer:
            return "[No response generated]"
        return answer

    def run(self):
        """Run the interactive chatbot"""
        if not self.running:
            print("\n✗ Chatbot could not be initialized. Exiting.")
            return
        
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\n" + "=" * 70)
                    print("Thank you for using TKRCET College Assistant!")
                    print("=" * 70 + "\n")
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                
                elif user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.print_welcome()
                
                elif user_input.lower() == 'status':
                    self.print_status()
                
                else:
                    # Process query through RAG system
                    print("\nAssistant: ", end="", flush=True)
                    
                    try:
                        answer = self.rag(user_input)
                        formatted_answer = self.format_answer(answer)
                        print(formatted_answer)
                    except Exception as e:
                        print(f"[Error processing query: {str(e)}]")
                    
                    print()
                
            except KeyboardInterrupt:
                print("\n\n" + "=" * 70)
                print("Chatbot interrupted. Goodbye!")
                print("=" * 70 + "\n")
                break
            except Exception as e:
                print(f"\n✗ Error: {str(e)}\n")


def main():
    """Main entry point"""
    chatbot = TerminalChatbot()
    chatbot.run()


if __name__ == '__main__':
    main()
