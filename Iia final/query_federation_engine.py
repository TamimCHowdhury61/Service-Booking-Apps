# from __future__ import annotations

# import json
# from pathlib import Path
# from typing import Any, Dict, List, Optional

# from distributed_database_manager import DistributedDatabaseManager
# from distributed_llm_service import DistributedLLMService


# class PromptRewriteEngine:
#     """Lightweight prompt normalizer used before federated queries are executed."""

#     REGION_HINTS = {
#         "northeast": ["boston", "new york", "philly", "philadelphia", "maine"],
#         "southeast": ["atlanta", "miami", "orlando", "charlotte"],
#         "midwest": ["chicago", "ohio", "detroit", "michigan"],
#         "southwest": ["texas", "houston", "dallas", "austin"],
#         "west": ["california", "seattle", "san francisco", "portland"],
#     }

#     def rewrite(self, user_query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
#         """Return a structured representation of the user's need."""
#         canonical_query = user_query.strip()
#         if not canonical_query:
#             canonical_query = analysis.get("description", "")

#         keywords = set(kw.lower() for kw in analysis.get("keywords", []) if kw)
#         keywords.update(self._extract_keywords(user_query))
#         region = self._detect_region(user_query) or analysis.get("location_preference", "")

#         provider_bias = analysis.get("recommended_provider_type", "both")

#         return {
#             "canonical_query": canonical_query,
#             "keywords": sorted(keywords),
#             "region": region or "",
#             "primary_intent": analysis.get("service_type", "general"),
#             "provider_bias": provider_bias,
#         }

#     def _extract_keywords(self, user_query: str) -> List[str]:
#         tokens = []
#         lowered = user_query.lower()
#         hints = {
#             "plumbing": ["plumb", "pipe", "leak"],
#             "electrical": ["electric", "wire", "breaker", "outlet"],
#             "painting": ["paint", "coating", "spray"],
#             "hvac": ["hvac", "cooling", "ac", "air condition", "vent"],
#             "landscaping": ["lawn", "yard", "landscape", "garden"],
#             "cleaning": ["clean", "janitor", "maid"],
#             "automotive": ["car", "auto", "vehicle", "engine"],
#             "carpentry": ["wood", "carpent", "cabinet"],
#         }
#         for keyword, signatures in hints.items():
#             if any(sig in lowered for sig in signatures):
#                 tokens.append(keyword)
#         return tokens

#     def _detect_region(self, user_query: str) -> Optional[str]:
#         lowered = user_query.lower()
#         for region, hints in self.REGION_HINTS.items():
#             if any(hint in lowered for hint in hints):
#                 return region
#         return None


# class ResearchCatalog:
#     """Loads company names captured during research so we can surface them alongside DB results."""

#     def __init__(self, dataset_path: Optional[Path] = None):
#         self.dataset_path = Path(dataset_path) if dataset_path else Path(__file__).with_name("research_company_profiles.json")
#         self.data: List[Dict[str, Any]] = []
#         self._load()

#     def _load(self):
#         if not self.dataset_path.exists():
#             return
#         try:
#             with self.dataset_path.open("r", encoding="utf-8") as handle:
#                 payload = json.load(handle)
#                 self.data = payload.get("companies", [])
#         except json.JSONDecodeError:
#             print("Warning: Could not parse research_company_profiles.json")

#     def match(self, service_focus: str) -> List[Dict[str, Any]]:
#         focus = (service_focus or "").lower()
#         matches = []
#         for entry in self.data:
#             categories = [c.lower() for c in entry.get("service_categories", [])]
#             if focus and focus != "general" and focus not in categories:
#                 continue
#             matches.append(entry)
#         return matches[:5]


# class QueryFederationEngine:
#     """Coordinates prompt rewriting, distributed querying, and result integration."""

#     def __init__(
#         self,
#         db_manager: DistributedDatabaseManager,
#         sorting_service,  # Remove type hint to avoid circular import
#         llm_service: Optional[DistributedLLMService] = None,
#     ):
#         self.db_manager = db_manager
#         self.sorting_service = sorting_service
#         self.llm_service = llm_service or DistributedLLMService()
#         self.prompt_rewriter = PromptRewriteEngine()
#         self.research_catalog = ResearchCatalog()

#     def run_federated_search(self, user_query: str, limit: int = 10) -> Dict[str, Any]:
#         analysis = self.llm_service.analyze_distributed_service_request(user_query, "both")
#         rewritten = self.prompt_rewriter.rewrite(user_query, analysis)
#         plan = self._build_federated_plan(analysis, rewritten)

#         search_results = self.db_manager.get_cross_laptop_results(plan["service_focus"], plan.get("region"))
#         if search_results.get("combined_results"):
#             sorted_results = self.sorting_service._apply_intelligent_sorting(  # pylint: disable=protected-access
#                 search_results.get("combined_results"),
#                 analysis,
#             )
#         else:
#             sorted_results = []

#         # Pass the raw search_results into the integrator (was referencing undefined raw_results)
#         integration_summary = self._integrate_results(sorted_results, search_results, plan, search_results)
#         research_highlights = self.research_catalog.match(plan["service_focus"])

#         return {
#             "analysis": analysis,
#             "rewritten_prompt": rewritten,
#             "plan": plan,
#             "results": sorted_results[:limit],
#             "integration_summary": integration_summary,
#             "research_highlights": research_highlights,
#         }

#     def _build_federated_plan(self, analysis: Dict[str, Any], rewritten: Dict[str, Any]) -> Dict[str, Any]:
#         service_focus = analysis.get("service_type") or rewritten.get("primary_intent") or "general"
#         region = rewritten.get("region") or analysis.get("location_preference") or ""
#         provider_scope = analysis.get("recommended_provider_type", "both")
#         keywords = rewritten.get("keywords", [])

#         base_filters = {
#             "service_focus": service_focus,
#             "region": region,
#             "keywords": keywords,
#             "urgency": analysis.get("urgency", "medium"),
#         }

#         primary_sql = f"SELECT * FROM companies WHERE business_type LIKE '%{service_focus}%' OR specialization_areas LIKE '%{service_focus}%';"
#         secondary_sql = f"SELECT * FROM EMPLOYEE WHERE job_type LIKE '%{service_focus}%';"

#         return {
#             "service_focus": service_focus,
#             "region": region,
#             "provider_scope": provider_scope,
#             "keywords": keywords,
#             "queries": [
#                 {"target": "primary", "filters": base_filters, "sql": primary_sql},
#                 {"target": "secondary", "filters": base_filters, "sql": secondary_sql},
#             ],
#             "rewritten_prompt": rewritten.get("canonical_query", ""),
#         }

#     def _integrate_results(
#         self,
#         sorted_results: List[Dict[str, Any]],
#         search_results: Dict[str, Any],
#         plan: Dict[str, Any],
#         raw_results: Dict[str, Any],
#     ) -> Dict[str, Any]:
#         """Integrate sorted results and raw counts from both databases into a summary."""
#         print("DEBUG: _integrate_results called with:")
#         print(f"  - sorted_results: {len(sorted_results)} items")
#         print(f"  - search_results keys: {list(search_results.keys())}")
#         print(f"  - plan keys: {list(plan.keys())}")
#         print(f"  - raw_results keys: {list(raw_results.keys())}")

#         primary_top = [r for r in sorted_results if r.get("data_source") == "Primary"][:3]
#         secondary_top = [r for r in sorted_results if r.get("data_source") == "Secondary"][:3]

#         coverage = {
#             "primary_matches": raw_results.get("companies_count", 0),
#             "secondary_matches": raw_results.get("employees_count", 0),
#             "combined": raw_results.get("total_count", 0),
#         }

#         integration_notes = []
#         if coverage["primary_matches"] and coverage["secondary_matches"]:
#             integration_notes.append("Results blended from both databases.")
#         elif coverage["primary_matches"]:
#             integration_notes.append("Primary catalog dominated the answers.")
#         elif coverage["secondary_matches"]:
#             integration_notes.append("Secondary catalog dominated the answers.")
#         else:
#             integration_notes.append("No live database matches were returned.")

#         if plan.get("region"):
#             integration_notes.append(f"Region bias applied: {plan['region']}")
#         if plan.get("provider_scope") and plan["provider_scope"] != "both":
#             integration_notes.append(f"Provider preference leaned toward {plan['provider_scope']} profiles.")

#         return {
#             "coverage": coverage,
#             "top_primary": [{"name": r.get("name"), "rating": r.get("rating")} for r in primary_top],
#             "top_secondary": [{"name": r.get("name"), "rating": r.get("rating")} for r in secondary_top],
#             "notes": integration_notes,
#         }
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from distributed_database_manager import DistributedDatabaseManager
from distributed_llm_service import DistributedLLMService


class PromptRewriteEngine:
    """Lightweight prompt normalizer used before federated queries are executed."""

    REGION_HINTS = {
        "northeast": ["boston", "new york", "philly", "philadelphia", "maine"],
        "southeast": ["atlanta", "miami", "orlando", "charlotte"],
        "midwest": ["chicago", "ohio", "detroit", "michigan"],
        "southwest": ["texas", "houston", "dallas", "austin"],
        "west": ["california", "seattle", "san francisco", "portland"],
    }

    def rewrite(self, user_query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Return a structured representation of the user's need."""
        canonical_query = user_query.strip()
        if not canonical_query:
            canonical_query = analysis.get("description", "")

        keywords = set(kw.lower() for kw in analysis.get("keywords", []) if kw)
        keywords.update(self._extract_keywords(user_query))
        region = self._detect_region(user_query) or analysis.get("location_preference", "")

        provider_bias = analysis.get("recommended_provider_type", "both")

        return {
            "canonical_query": canonical_query,
            "keywords": sorted(keywords),
            "region": region or "",
            "primary_intent": analysis.get("service_type", "general"),
            "provider_bias": provider_bias,
        }

    def _extract_keywords(self, user_query: str) -> List[str]:
        tokens: List[str] = []
        lowered = user_query.lower()
        hints = {
            "plumbing": ["plumb", "pipe", "leak"],
            "electrical": ["electric", "wire", "breaker", "outlet"],
            "painting": ["paint", "coating", "spray"],
            "hvac": ["hvac", "cooling", "ac", "air condition", "vent"],
            "landscaping": ["lawn", "yard", "landscape", "garden"],
            "cleaning": ["clean", "janitor", "maid"],
            "automotive": ["car", "auto", "vehicle", "engine"],
            "carpentry": ["wood", "carpent", "cabinet"],
        }
        for keyword, signatures in hints.items():
            if any(sig in lowered for sig in signatures):
                tokens.append(keyword)
        return tokens

    def _detect_region(self, user_query: str) -> Optional[str]:
        lowered = user_query.lower()
        for region, hints in self.REGION_HINTS.items():
            if any(hint in lowered for hint in hints):
                return region
        return None


class ResearchCatalog:
    """Loads company names captured during research so we can surface them alongside DB results."""

    def __init__(self, dataset_path: Optional[Path] = None):
        self.dataset_path = (
            Path(dataset_path)
            if dataset_path
            else Path(__file__).with_name("research_company_profiles.json")
        )
        self.data: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self.dataset_path.exists():
            return
        try:
            with self.dataset_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
                self.data = payload.get("companies", [])
        except json.JSONDecodeError:
            print("Warning: Could not parse research_company_profiles.json")

    def match(self, service_focus: str) -> List[Dict[str, Any]]:
        focus = (service_focus or "").lower()
        matches: List[Dict[str, Any]] = []
        for entry in self.data:
            categories = [c.lower() for c in entry.get("service_categories", [])]
            if focus and focus != "general" and focus not in categories:
                continue
            matches.append(entry)
        return matches[:5]


class QueryFederationEngine:
    """Coordinates prompt rewriting, distributed querying, and result integration."""

    def __init__(
        self,
        db_manager: DistributedDatabaseManager,
        sorting_service,  # avoid circular import; must expose _apply_intelligent_sorting
        llm_service: Optional[DistributedLLMService] = None,
    ):
        self.db_manager = db_manager
        self.sorting_service = sorting_service
        self.llm_service = llm_service or DistributedLLMService()
        self.prompt_rewriter = PromptRewriteEngine()
        self.research_catalog = ResearchCatalog()

    # --------------------------------------------------------------------- #
    # PUBLIC API
    # --------------------------------------------------------------------- #
    def run_federated_search(self, user_query: str, limit: int = 10) -> Dict[str, Any]:
        """
        End-to-end federated search:
        - LLM analysis
        - prompt rewrite
        - distributed DB query
        - intelligent sorting
        - integration summary
        """
        # 1) Analyze the request
        analysis = self.llm_service.analyze_distributed_service_request(
            user_query, "both"
        )

        # 2) Rewrite the prompt into a structured representation
        rewritten = self.prompt_rewriter.rewrite(user_query, analysis)

        # 3) Build a federated plan (for introspection / debugging)
        plan = self._build_federated_plan(analysis, rewritten)

        # 4) Hit both databases via the distributed DB manager
        search_results = self.db_manager.get_cross_laptop_results(
            plan["service_focus"], plan.get("region")
        )  # -> {companies, employees, combined_results, counts...}

        combined = search_results.get("combined_results", []) or []

        # 5) Apply intelligent sorting over the normalized combined results
        if combined:
            sorted_results = self.sorting_service._apply_intelligent_sorting(  # pylint: disable=protected-access
                combined,
                analysis,
            )
        else:
            sorted_results = []

        # 6) Integrate results into a compact summary
        integration_summary = self._integrate_results(
            sorted_results, search_results, plan, search_results
        )

        # 7) Optional: attach external research highlights
        research_highlights = self.research_catalog.match(plan["service_focus"])

        # 8) Derive some cheap meta-signals for the UI
        coverage = integration_summary.get("coverage", {})
        recommendation_confidence = float(analysis.get("confidence_score", 0.0))

        query_text = rewritten.get("canonical_query") or user_query or ""
        words = query_text.split()
        query_complexity = {
            "word_count": len(words),
            "has_location_hint": bool(rewritten.get("region")),
            "has_urgency_hint": analysis.get("urgency", "medium") in {
                "high",
                "emergency",
            },
            "complexity_level": self._infer_complexity_level(len(words)),
        }

        # Return shape is rich but backward-compatible
        return {
            # core analysis information
            "analysis": analysis,
            "rewritten_prompt": rewritten,
            "plan": plan,
            # raw DB view (includes companies/employees counts)
            "search_results": search_results,
            # sorted, normalized providers: this is what the GUI should render
            "sorted_results": sorted_results,
            # deprecated / backward-compat aliases
            "results": sorted_results[:limit],
            "combined_results": sorted_results,
            # summaries & meta
            "integration_summary": integration_summary,
            "search_coverage": coverage,
            "recommendation_confidence": recommendation_confidence,
            "query_complexity": query_complexity,
            "research_highlights": research_highlights,
        }

    # --------------------------------------------------------------------- #
    # INTERNAL HELPERS
    # --------------------------------------------------------------------- #
    def _infer_complexity_level(self, word_count: int) -> str:
        if word_count <= 4:
            return "simple"
        if word_count <= 12:
            return "moderate"
        return "complex"

    def _build_federated_plan(
        self, analysis: Dict[str, Any], rewritten: Dict[str, Any]
    ) -> Dict[str, Any]:
        service_focus = (
            analysis.get("service_type")
            or rewritten.get("primary_intent")
            or "general"
        )
        region = (
            rewritten.get("region")
            or analysis.get("location_preference")
            or ""
        )
        provider_scope = analysis.get("recommended_provider_type", "both")
        keywords = rewritten.get("keywords", [])

        base_filters = {
            "service_focus": service_focus,
            "region": region,
            "keywords": keywords,
            "urgency": analysis.get("urgency", "medium"),
        }

        # NOTE: These SQL strings are *informational only* (not executed here).
        primary_sql = (
            "SELECT * FROM companies "
            f"WHERE business_type LIKE '%{service_focus}%' "
            f"OR specialization_areas LIKE '%{service_focus}%';"
        )
        secondary_sql = (
            "SELECT * FROM EMPLOYEE "
            f"WHERE job_type LIKE '%{service_focus}%';"
        )

        return {
            "service_focus": service_focus,
            "region": region,
            "provider_scope": provider_scope,
            "keywords": keywords,
            "queries": [
                {"target": "primary", "filters": base_filters, "sql": primary_sql},
                {"target": "secondary", "filters": base_filters, "sql": secondary_sql},
            ],
            "rewritten_prompt": rewritten.get("canonical_query", ""),
        }

    def _integrate_results(
        self,
        sorted_results: List[Dict[str, Any]],
        search_results: Dict[str, Any],
        plan: Dict[str, Any],
        raw_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Integrate sorted results and raw counts from both databases into a summary."""
        print("DEBUG: _integrate_results called with:")
        print(f"  - sorted_results: {len(sorted_results)} items")
        print(f"  - search_results keys: {list(search_results.keys())}")
        print(f"  - plan keys: {list(plan.keys())}")
        print(f"  - raw_results keys: {list(raw_results.keys())}")

        primary_top = [r for r in sorted_results if r.get("data_source") == "Primary"][
            :3
        ]
        secondary_top = [
            r for r in sorted_results if r.get("data_source") == "Secondary"
        ][:3]

        coverage = {
            "primary_matches": raw_results.get("companies_count", 0),
            "secondary_matches": raw_results.get("employees_count", 0),
            "combined": raw_results.get("total_count", 0),
        }

        integration_notes: List[str] = []
        if coverage["primary_matches"] and coverage["secondary_matches"]:
            integration_notes.append("Results blended from both databases.")
        elif coverage["primary_matches"]:
            integration_notes.append("Primary catalog dominated the answers.")
        elif coverage["secondary_matches"]:
            integration_notes.append("Secondary catalog dominated the answers.")
        else:
            integration_notes.append("No live database matches were returned.")

        if plan.get("region"):
            integration_notes.append(f"Region bias applied: {plan['region']}")
        if plan.get("provider_scope") and plan["provider_scope"] != "both":
            integration_notes.append(
                f"Provider preference leaned toward {plan['provider_scope']} profiles."
            )

        return {
            "coverage": coverage,
            "top_primary": [
                {"name": r.get("name"), "rating": r.get("rating")} for r in primary_top
            ],
            "top_secondary": [
                {"name": r.get("name"), "rating": r.get("rating")}
                for r in secondary_top
            ],
            "notes": integration_notes,
        }
