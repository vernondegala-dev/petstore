import argparse
import sys
import os
from dotenv import load_dotenv

# Add project root to path if needed to ensure we can import api_client and agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.qa_agent import QATestingAgent

# Load local environment variables from .env if present
load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="Run the Autonomous QA Testing Agent for Swagger Petstore API."
    )
    parser.add_argument(
        "objective",
        type=str,
        help="The high-level testing objective / prompt for the agent. E.g., 'Verify pet inventory API and place a temporary order to see if inventory updates'"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="Google Gemini model name to use. Default is 'gemini-2.5-flash'."
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="https://petstore.swagger.io/v2",
        help="Base URL of the Petstore API to test. Default is 'https://petstore.swagger.io/v2'."
    )

    args = parser.parse_args()

    # Double check API Key presence
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("API_KEY"):
        print("⚠️  Warning: Neither GEMINI_API_KEY nor API_KEY environment variables are set.")
        print("   The Google GenAI client might fail to initialize or prompt for an API key.")
        print("   Please export GEMINI_API_KEY before running, e.g.:")
        print("   export GEMINI_API_KEY='your-key-here'\n")

    print("🚀 Initializing QATestingAgent...")
    agent = QATestingAgent(base_url=args.base_url, model_name=args.model)
    
    try:
        report = agent.run(args.objective)
        print("\n" + "="*50)
        print("📝 AGENT FINAL TESTING REPORT")
        print("="*50)
        print(report)
        print("="*50)
    except Exception as e:
        print(f"❌ Error running QA Agent: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
