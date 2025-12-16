#!/usr/bin/env python3
"""
Demo: String Similarity Matching for Database Federation

Shows how Jaro-Winkler-like string similarity detection works
to deduplicate and match providers across federated databases.
"""

from string_similarity_matcher import StringSimplicityMatcher


def demo_similarity_scoring():
    """Demonstrate string similarity scoring"""
    print("=" * 70)
    print("DEMO 1: String Similarity Scoring (Jaro-Winkler-like)")
    print("=" * 70)

    test_pairs = [
        ("Blue Peak Plumbing", "Blue Peak Plumbing LLC"),
        ("John's Electrical Services", "Johns Electrical Service"),
        ("ABC Painting Company", "ABC Paint"),
        ("Quick Plumbing Repair", "Rapid Plumbing Services"),
        ("XYZ Corp", "123 Corp"),
    ]

    for name1, name2 in test_pairs:
        similarity = StringSimplicityMatcher.calculate_similarity(name1, name2)
        status = "✅ LIKELY MATCH" if similarity >= 0.80 else "⚠️ POSSIBLE MATCH" if similarity >= 0.70 else "❌ NO MATCH"
        print(f"\n'{name1}'")
        print(f"  vs")
        print(f"'{name2}'")
        print(f"  Similarity: {similarity:.1%} {status}")


def demo_duplicate_detection():
    """Demonstrate duplicate detection across federated databases"""
    print("\n" + "=" * 70)
    print("DEMO 2: Duplicate Detection Across Federated Databases")
    print("=" * 70)

    # Simulate results from two databases
    primary_results = [
        {
            "id": 1,
            "name": "Blue Peak Plumbing Co.",
            "data_source": "Primary",
            "rating": 4.8,
            "total_reviews": 150,
            "type": "Company"
        },
        {
            "id": 2,
            "name": "Elite Electrical Solutions",
            "data_source": "Primary",
            "rating": 4.6,
            "total_reviews": 120,
            "type": "Company"
        },
    ]

    secondary_results = [
        {
            "id": 101,
            "name": "Blue Peak Plumbing LLC",
            "data_source": "Secondary",
            "rating": 4.7,
            "total_orders": 98,
            "type": "Individual Worker"
        },
        {
            "id": 102,
            "name": "Elite Electrical Services",
            "data_source": "Secondary",
            "rating": 4.5,
            "total_orders": 75,
            "type": "Individual Worker"
        },
        {
            "id": 103,
            "name": "Sunrise HVAC Repair",
            "data_source": "Secondary",
            "rating": 4.3,
            "total_orders": 60,
            "type": "Individual Worker"
        },
    ]

    combined = primary_results + secondary_results

    print(f"\nInitial combined results: {len(combined)} providers")
    print("  Primary database: 2 companies")
    print("  Secondary database: 3 workers")

    # Find duplicates
    duplicates = StringSimplicityMatcher.find_duplicates_in_results(combined, similarity_threshold=0.80)

    print(f"\nDuplicates detected: {len(duplicates)}")
    for idx1, idx2, similarity in duplicates:
        r1 = combined[idx1]
        r2 = combined[idx2]
        print(f"\n  ✓ Potential duplicate pair (similarity: {similarity:.1%}):")
        print(f"    - '{r1['name']}' ({r1['data_source']} DB, rating: {r1['rating']})")
        print(f"    - '{r2['name']}' ({r2['data_source']} DB, rating: {r2['rating']})")

    # Deduplicate
    deduplicated, merges = StringSimplicityMatcher.deduplicate_federated_results(
        combined,
        similarity_threshold=0.80,
        keep_strategy="highest_rated"
    )

    print(f"\nAfter deduplication:")
    print(f"  Deduplicated results: {len(deduplicated)} providers")
    print(f"  Duplicates removed: {len(merges)}")
    print(f"\nRemaining providers:")
    for r in deduplicated:
        print(f"  - {r['name']} ({r['data_source']} DB, rating: {r['rating']})")


def demo_similarity_report():
    """Demonstrate similarity report generation"""
    print("\n" + "=" * 70)
    print("DEMO 3: Similarity Report (for admin/monitoring)")
    print("=" * 70)

    combined = [
        {
            "id": 1,
            "name": "ABC Plumbing",
            "data_source": "Primary",
            "rating": 4.5,
        },
        {
            "id": 2,
            "name": "ABC Plumbing Services",
            "data_source": "Secondary",
            "rating": 4.6,
        },
        {
            "id": 3,
            "name": "XYZ Electrical",
            "data_source": "Primary",
            "rating": 4.7,
        },
        {
            "id": 4,
            "name": "General Services",
            "data_source": "Secondary",
            "rating": 4.2,
        },
    ]

    report = StringSimplicityMatcher.get_similarity_report(combined, similarity_threshold=0.80)

    print(f"\nTotal results: {report['total_results']}")
    print(f"Total duplicates found: {report['total_duplicates_found']}")
    print(f"Confirmed duplicates (>90% similar): {report['confirmed_duplicates']}")
    print(f"Possible duplicates (80-90% similar): {report['possible_duplicates']}")

    if report['duplicate_details']:
        print(f"\nDuplicate details:")
        for detail in report['duplicate_details']:
            print(
                f"  - '{detail['name1']}' ({detail['source1']}) vs "
                f"'{detail['name2']}' ({detail['source2']}): {detail['similarity']:.1%} similar"
            )


def demo_output_unchanged():
    """Demonstrate that visible output is unchanged"""
    print("\n" + "=" * 70)
    print("DEMO 4: Output Remains Unchanged for End Users")
    print("=" * 70)

    print("\n✅ Key points:")
    print("  1. Deduplication happens INTERNALLY in get_cross_laptop_results()")
    print("  2. UI shows deduplicated results (cleaner, no duplicates)")
    print("  3. No API changes - output structure is identical")
    print("  4. Metadata stored internally (_deduplication_report) - NOT shown in UI")
    print("  5. Sorting/ranking still applies as before")
    print("  6. Admin can optionally view dedup report for monitoring")


if __name__ == "__main__":
    demo_similarity_scoring()
    demo_duplicate_detection()
    demo_similarity_report()
    demo_output_unchanged()

    print("\n" + "=" * 70)
    print("✅ All demos completed successfully!")
    print("=" * 70)
    print("\nSummary:")
    print("  - Uses difflib.SequenceMatcher (similar to Jaro-Winkler)")
    print("  - Detects duplicates across federated databases (Primary vs Secondary)")
    print("  - Removes likely duplicates based on similarity threshold")
    print("  - Keeps entry with highest rating when duplicates are found")
    print("  - Deduplication is transparent to the UI/end users")
