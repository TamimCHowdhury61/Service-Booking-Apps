"""
String Similarity and Deduplication Matcher using Jaro-Winkler-like approach.
Uses difflib.SequenceMatcher for similarity matching and deduplication across federated databases.
"""

import difflib
from typing import Dict, List, Tuple, Any
from decimal import Decimal


class StringSimplicityMatcher:
    """
    Provides string similarity matching and provider deduplication for federated search.
    Uses difflib.SequenceMatcher (similar to Jaro-Winkler approach).
    """

    # Similarity threshold for detecting duplicates (0.0 to 1.0)
    DEFAULT_SIMILARITY_THRESHOLD = 0.80

    # Similarity threshold for detecting possible duplicates (to flag for review)
    POSSIBLE_DUPLICATE_THRESHOLD = 0.70

    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate string similarity score between 0.0 and 1.0.
        Uses difflib.SequenceMatcher for consistent, efficient matching.

        Args:
            str1: First string to compare
            str2: Second string to compare

        Returns:
            Similarity score (0.0 = no match, 1.0 = identical)
        """
        if not str1 or not str2:
            return 0.0

        # Normalize strings: lowercase, strip whitespace
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()

        # Quick check for exact match
        if s1 == s2:
            return 1.0

        # Calculate similarity using SequenceMatcher (similar to Jaro-Winkler logic)
        matcher = difflib.SequenceMatcher(None, s1, s2)
        return matcher.ratio()

    @staticmethod
    def are_duplicates(
        name1: str,
        name2: str,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> bool:
        """
        Determine if two provider names likely refer to the same entity.

        Args:
            name1: First provider name
            name2: Second provider name
            similarity_threshold: Threshold for considering a match (default 0.80)

        Returns:
            True if providers are likely duplicates, False otherwise
        """
        similarity = StringSimplicityMatcher.calculate_similarity(name1, name2)
        return similarity >= similarity_threshold

    @staticmethod
    def find_duplicates_in_results(
        combined_results: List[Dict[str, Any]],
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> List[Tuple[int, int, float]]:
        """
        Find potential duplicate providers in combined results from both databases.

        Args:
            combined_results: List of provider dictionaries from federated search
            similarity_threshold: Threshold for flagging duplicates

        Returns:
            List of tuples: (index1, index2, similarity_score) for potential duplicates
        """
        duplicates = []

        for i in range(len(combined_results)):
            for j in range(i + 1, len(combined_results)):
                result_i = combined_results[i]
                result_j = combined_results[j]

                # Only cross-check between different data sources
                if result_i.get("data_source") == result_j.get("data_source"):
                    continue

                name_i = result_i.get("name", "")
                name_j = result_j.get("name", "")

                similarity = StringSimplicityMatcher.calculate_similarity(name_i, name_j)

                if similarity >= similarity_threshold:
                    duplicates.append((i, j, similarity))

        return duplicates

    @staticmethod
    def deduplicate_federated_results(
        combined_results: List[Dict[str, Any]],
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        keep_strategy: str = "highest_rated",
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Deduplicate federated results by identifying duplicates across databases.
        Returns deduplicated list and a list of merged duplicates (for reference).

        Args:
            combined_results: List of provider dictionaries
            similarity_threshold: Threshold for detecting duplicates
            keep_strategy: Strategy for keeping one entry when duplicates found
                - 'highest_rated': Keep the entry with highest rating
                - 'primary_first': Keep the entry from primary database (Company)
                - 'most_reviews': Keep the entry with most reviews/orders

        Returns:
            Tuple of (deduplicated_results, duplicate_merges_metadata)
        """
        if not combined_results:
            return [], []

        # Find duplicates
        duplicates = StringSimplicityMatcher.find_duplicates_in_results(
            combined_results, similarity_threshold
        )

        if not duplicates:
            return combined_results, []

        # Track which indices to remove
        to_remove = set()
        duplicate_merges = []

        for idx1, idx2, similarity in duplicates:
            if idx1 in to_remove or idx2 in to_remove:
                continue  # Already marked for removal

            result1 = combined_results[idx1]
            result2 = combined_results[idx2]

            # Determine which to keep based on strategy
            if keep_strategy == "highest_rated":
                rating1 = float(result1.get("rating", 0))
                rating2 = float(result2.get("rating", 0))
                keep_idx, remove_idx = (idx1, idx2) if rating1 >= rating2 else (idx2, idx1)

            elif keep_strategy == "primary_first":
                # Primary database (companies) take precedence
                is_primary1 = result1.get("data_source") == "Primary"
                is_primary2 = result2.get("data_source") == "Primary"
                if is_primary1 and not is_primary2:
                    keep_idx, remove_idx = idx1, idx2
                elif is_primary2 and not is_primary1:
                    keep_idx, remove_idx = idx2, idx1
                else:
                    # Both same source, use rating
                    rating1 = float(result1.get("rating", 0))
                    rating2 = float(result2.get("rating", 0))
                    keep_idx, remove_idx = (idx1, idx2) if rating1 >= rating2 else (idx2, idx1)

            elif keep_strategy == "most_reviews":
                reviews1 = result1.get("total_reviews", result1.get("total_orders", 0))
                reviews2 = result2.get("total_reviews", result2.get("total_orders", 0))
                keep_idx, remove_idx = (idx1, idx2) if reviews1 >= reviews2 else (idx2, idx1)

            else:
                keep_idx, remove_idx = idx1, idx2

            to_remove.add(remove_idx)

            # Record the merge for reference
            duplicate_merges.append({
                "kept": combined_results[keep_idx].get("name", "Unknown"),
                "kept_source": combined_results[keep_idx].get("data_source", "Unknown"),
                "removed": combined_results[remove_idx].get("name", "Unknown"),
                "removed_source": combined_results[remove_idx].get("data_source", "Unknown"),
                "similarity": round(similarity, 3),
            })

        # Create deduplicated results
        deduplicated = [r for i, r in enumerate(combined_results) if i not in to_remove]

        return deduplicated, duplicate_merges

    @staticmethod
    def enhance_result_with_cross_source_info(
        result: Dict[str, Any], other_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhance a result with information from similar entries in other data sources.
        Used to combine metadata from similar providers across databases.

        Args:
            result: Provider result from one database
            other_sources: List of results from other database sources

        Returns:
            Enhanced result with additional metadata
        """
        name = result.get("name", "")
        similarity_threshold = 0.75

        # Find similar entries from other sources
        similar_entries = []
        for other in other_sources:
            if other.get("data_source") == result.get("data_source"):
                continue

            similarity = StringSimplicityMatcher.calculate_similarity(
                name, other.get("name", "")
            )

            if similarity >= similarity_threshold:
                similar_entries.append({"entry": other, "similarity": similarity})

        # Sort by similarity (highest first)
        similar_entries.sort(key=lambda x: x["similarity"], reverse=True)

        # Add cross-source info
        if similar_entries:
            best_match = similar_entries[0]["entry"]
            result["cross_source_match"] = {
                "matched_name": best_match.get("name"),
                "matched_source": best_match.get("data_source"),
                "similarity": round(similar_entries[0]["similarity"], 3),
                "combined_rating": round(
                    (
                        float(result.get("rating", 0))
                        + float(best_match.get("rating", 0))
                    )
                    / 2,
                    2,
                ),
            }

            result["found_in_both_sources"] = True

        return result

    @staticmethod
    def get_similarity_report(
        combined_results: List[Dict[str, Any]],
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> Dict[str, Any]:
        """
        Generate a detailed report of similarity matching and deduplication.

        Args:
            combined_results: List of provider results
            similarity_threshold: Threshold for duplicate detection

        Returns:
            Dictionary with similarity report
        """
        duplicates = StringSimplicityMatcher.find_duplicates_in_results(
            combined_results, similarity_threshold
        )

        possible_duplicates = [
            d
            for d in duplicates
            if d[2] >= similarity_threshold and d[2] < (similarity_threshold + 0.10)
        ]

        confirmed_duplicates = [d for d in duplicates if d[2] >= (similarity_threshold + 0.10)]

        return {
            "total_results": len(combined_results),
            "total_duplicates_found": len(duplicates),
            "possible_duplicates": len(possible_duplicates),
            "confirmed_duplicates": len(confirmed_duplicates),
            "duplicate_details": [
                {
                    "name1": combined_results[d[0]].get("name"),
                    "name2": combined_results[d[1]].get("name"),
                    "source1": combined_results[d[0]].get("data_source"),
                    "source2": combined_results[d[1]].get("data_source"),
                    "similarity": round(d[2], 3),
                }
                for d in duplicates
            ],
        }
