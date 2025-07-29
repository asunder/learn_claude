#!/usr/bin/env python3
"""
Simple test for the Hypervisor Agent
"""

from hypervisor_agent import HypervisorAgent


def main():
    """Run simple test"""
    print("Testing Hypervisor Agent")
    print("=" * 40)
    
    try:
        agent = HypervisorAgent()
        
        # Test basic functionality
        print("\nCloud Providers:")
        for provider_key, provider in agent.cloud_providers.items():
            print(f"- {provider.name} ({provider_key.upper()})")
        
        print(f"\nHelp Categories:")
        categories = agent.get_help_categories()
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        print(f"\nHypervisors:")
        for hyp_name, hyp_info in agent.hypervisors.items():
            print(f"- {hyp_name.upper()}: {', '.join(hyp_info['products'][:2])}...")
        
        # Test query suggestions
        print(f"\nTesting Sample Query:")
        query = "How do I create a Terraform configuration for AWS EC2?"
        result = agent.suggest_solution(query, 'aws')
        print(f"Query: {result['query']}")
        print(f"Provider: {result['provider']}")
        print(f"Recommendations: {len(result['recommendations'])} items")
        if result['recommendations']:
            for rec in result['recommendations']:
                print(f"  - {rec}")
        
        print(f"\nCode examples: {len(result['code_examples'])} items")
        if result['code_examples']:
            print("First example snippet:")
            print(result['code_examples'][0][:200] + "...")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)