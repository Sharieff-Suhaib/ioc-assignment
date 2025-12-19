from agent.clinical_agent import create_agent
from utils.config import config
import json

def print_separator():
    print("\n" + "="*80 + "\n")

def format_result(result:  dict):
    """Pretty print results"""
    if result['status'] == 'success': 
        print("✅ SUCCESS")
        print("\nSummary:")
        print(result['summary'])
        print("\nDetailed Results:")
        print(json.dumps(result['workflow_results'], indent=2, default=str))
    elif result['status'] == 'refused':
        print("❌ REFUSED")
        print(f"Reason: {result['reason']}")
    else:
        print("⚠️ ERROR")
        print(f"Error: {result. get('error')}")
    
    print(f"\n📋 Request ID: {result['request_id']}")

def main():
    print("🏥 Clinical Workflow Automation Agent")
    print("="*80)
    print(f"Model: mistralai/Mistral-7B-Instruct-v0.2")
    print(f"Mode: {'🧪 DRY RUN' if config.DRY_RUN_MODE else '🚀 LIVE'}")
    print_separator()
    
    print("Initializing agent...")
    agent = create_agent()
    print("✓ Agent initialized successfully")
    print_separator()
    
    test_cases = [
        "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility",
        "Find me available orthopedics slots for next month for patient Priya Sharma",
        "What medication should I prescribe for high blood pressure?",  # Should refuse
        "Search for patient Ravi Kumar and check his insurance status"
    ]
    
    print("🧪 Running Test Cases.. .\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        print(f"📝 Input: {test_input}")
        print("-" * 80)
        
        result = agent.process_request(test_input)
        format_result(result)
        
        print_separator()
    
    print("\n🎯 Interactive Mode - Try your own requests!")
    print("Examples:")
    print("  - Schedule cardiology appointment for Ravi Kumar")
    print("  - Check insurance for patient P001")
    print("  - Find orthopedics slots next week")
    print("\nType 'exit' to quit")
    print_separator()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent Processing...")
            result = agent.process_request(user_input)
            format_result(result)
            
        except KeyboardInterrupt: 
            print("\n\n👋 Goodbye!")
            break
        except Exception as e: 
            print(f"\n⚠️ Error: {e}")

if __name__ == "__main__":
    main()