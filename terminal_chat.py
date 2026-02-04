#!/usr/bin/env python3
"""
TKRCET College Buddy - Terminal Chat Interface
Unified interface for interacting with the MCP-based agent
"""

import os
import sys
import logging
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.ERROR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 70)
    print("TKRCET COLLEGE ASSISTANT - MCP POWERED")
    print("=" * 70)
    print("Initializing system components...")

def main():
    clear_screen()
    print_header()
    
    try:
        # Import agent
        from app.services.agent_mcp import SimplifiedMCPAgent
        
        # Initialize
        agent = SimplifiedMCPAgent()
        print("\n✓ System Ready! Start chatting below.")
        print("-" * 70)
        print("Type 'exit' or 'quit' to close.")
        print("-" * 70 + "\n")
        
        # Chat loop
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit']:
                    print("\nGoodbye! Have a great day! 👋")
                    break
                
                # Get response
                print("\nAssistant: ", end="", flush=True)
                response = agent(user_input)
                print(response)
                print("-" * 30)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Have a great day! 👋")
                break
            except Exception as e:
                print(f"\nError: {e}")
                
    except ImportError as e:
        print(f"\n❌ Error: Could not import required modules. {e}")
        print("Make sure you are running from the project root and virtual environment is active.")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
