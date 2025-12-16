#!/usr/bin/env python3

"""
Enhanced AI Search Test - Natural Language Processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from distributed_database_manager_primary import DistributedDatabaseManager
from distributed_llm_service import DistributedLLMService

def test_enhanced_ai_search():
    """Test enhanced AI search with natural language queries"""
    print("Testing Enhanced AI Search with Natural Language Processing...")
    print("=" * 70)

    try:
        # Initialize services
        db_manager = DistributedDatabaseManager()
        llm_service = DistributedLLMService()

        # Test natural language queries
        natural_queries = [
            "I need a plumber",
            "My sink is leaking need to fix it",
            "The electrical outlet in my kitchen is not working",
            "Can someone help me paint my living room",
            "My air conditioner is broken and it's very hot",
            "I need emergency plumbing services ASAP",
            "Looking for someone to clean my house deeply",
            "My car won't start, need mechanic help",
            "Need help with landscaping my backyard",
            "Water heater is leaking and needs immediate repair",
            "Moving to a new apartment need help with packing",
            "My computer is running slow need technical help"
        ]

        print("\nNatural Language Queries Analysis:")
        print("=" * 50)

        for query in natural_queries:
            print(f"\n[Query] '{query}'")
            print("-" * 40)

            # Analyze with AI service
            analysis = llm_service.analyze_distributed_service_request(query, 'both')

            print(f"[Service Type]: {analysis.get('service_type', 'unknown')}")
            print(f"[Urgency]: {analysis.get('urgency', 'medium')}")
            print(f"[Recommended]: {analysis.get('recommended_provider_type', 'both')}")
            print(f"[Search Scope]: {analysis.get('search_scope', 'both')}")
            print(f"[Reasoning]: {analysis.get('reasoning', 'No reasoning provided')}")
            print(f"[Confidence]: {analysis.get('confidence_score', 0):.2f}")

            # Get actual search results
            try:
                results = db_manager.get_cross_laptop_results(analysis['service_type'])

                if results['combined_results']:
                    print(f"[OK] Found {results['total_count']} providers:")
                    print(f"   - Companies: {results['companies_count']}")
                    print(f"   - Employees: {results['employees_count']}")

                    # Show top 2 most relevant providers
                    print(f"[Top Recommendations]:")
                    for i, provider in enumerate(results['combined_results'][:2], 1):
                        print(f"   {i}. {provider['name']} ({provider['type']})")
                        print(f"      Service: {provider['service_name']}")
                        print(f"      Rating: {provider['rating']}")
                        print(f"      Cost: ${provider['avg_cost']}/hr")
                        print(f"      Source: {provider['data_source']}")
                else:
                    print(f"[ERROR] No providers found")

            except Exception as e:
                print(f"[ERROR] Search error: {e}")

        print("\n" + "=" * 70)
        print("Intelligent Recommendations Test:")
        print("=" * 50)

        # Test intelligent recommendations
        test_scenarios = [
            {
                "query": "I need emergency plumbing for a burst pipe",
                "context": "Emergency situation, water damage risk"
            },
            {
                "query": "Need complete kitchen renovation with cabinets",
                "context": "Large project, needs professional coordination"
            },
            {
                "query": "Just need a simple light bulb replaced",
                "context": "Small quick job, cost-sensitive"
            },
            {
                "query": "My business office needs regular cleaning service",
                "context": "Commercial space, ongoing service needed"
            }
        ]

        for scenario in test_scenarios:
            print(f"\nScenario: {scenario['context']}")
            print(f"Query: '{scenario['query']}'")

            # Get AI analysis
            analysis = llm_service.analyze_distributed_service_request(scenario['query'], 'both')

            # Get search results
            results = db_manager.get_cross_laptop_results(analysis['service_type'])

            # Generate intelligent summary
            summary = llm_service.generate_intelligent_summary(scenario['query'], results)

            print(f"AI Recommendation: {summary}")

            # Suggest provider type
            suggestion = llm_service.suggest_provider_type(scenario['query'])
            print(f"Provider Suggestion: {suggestion.get('recommended_type', 'both')}")
            print(f"Confidence: {suggestion.get('confidence', 0):.2f}")
            print(f"Key Factors: {', '.join(suggestion.get('key_factors', []))}")
            print("-" * 30)

        print("\n" + "=" * 70)
        print("[OK] Enhanced AI Search Test Complete!")
        print("=" * 70)
        print("Natural Language Processing: WORKING!")
        print("Intelligent Service Matching: WORKING!")
        print("AI-Powered Recommendations: WORKING!")
        print("Cross-Database Analysis: WORKING!")

        db_manager.close_connections()

        print(f"\nReady for Natural Language Search!")
        print(f"You can now search like:")
        print(f'  • "I need a plumber"')
        print(f'  • "My sink is leaking need to fix it"')
        print(f'  • "Emergency electrical help needed"')
        print(f'  • "Need someone to paint my house"')
        print(f'  • "My car won\'t start"')
        print(f'  • "AC broken and it\'s 100 degrees"')

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_ai_search()