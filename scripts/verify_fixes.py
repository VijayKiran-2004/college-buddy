
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.agent_mcp import SimplifiedMCPAgent
from app.services.mcp_tools import CollegeMCPTools

print("="*60)
print("VERIFICATION SCRIPT: Model, SQL & Scraper Fixes")
print("="*60)

# 1. Initialize Agent (Checks Model)
print("\n[1] Testing Agent Initialization & Model Check...")
agent = SimplifiedMCPAgent()

# 2. Test SQL Query (Checks Database + Error Handling)
print("\n[2] Testing SQL Database Access...")
sql_query = "how many students got placed?"
print(f"Query: {sql_query}")
tools = CollegeMCPTools()
result = tools.query_database(sql_query)
print(f"Result Success: {result.get('success')}")
print(f"Result Data Preview: {str(result.get('data'))[:200]}...")

# 3. Test Scraper with Headers (Checks MalCare Bypass)
print("\n[3] Testing Scraper (MalCare Bypass)...")
# We'll use the tool directly to see if it works or falls back
scrape_result = tools.scrape_placements()
print(f"Scrape Success: {scrape_result.get('success')}")
content = scrape_result.get('data', {}).get('content', '')
if "MalCare" in content or "Firewall" in content:
    print("❌ STILL BLOCKED by MalCare")
else:
    print("✅ Scraper working / Fallback active")
    print(f"Content Preview: {content[:100]}...")

print("\n" + "="*60)
