# import json
# import re
# import logging
# from typing import Any, Dict, List

# import requests

# from config import LLM_CONFIG, SERVICE_SORTING_WEIGHTS, SERVICE_TYPES

# logger = logging.getLogger(__name__)


# class DistributedLLMService:
#     def __init__(self):
#         self.api_key = LLM_CONFIG['api_key']
#         self.model = LLM_CONFIG['model']
#         self.base_url = LLM_CONFIG.get('base_url', 'https://openrouter.ai/api/v1/chat/completions')
#         self.use_mock_service = False  # Use real OpenRouter API instead of mock

#     def _make_api_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
#         """Make API request to Google Gemini API"""
#         # If configured to use the mock service or no API key is provided, return a fallback immediately
#         if self.use_mock_service or not self.api_key:
#             return {
#                 "choices": [{
#                     "message": {
#                         "content": json.dumps(self._get_fallback_response(messages))
#                     }
#                 }]
#             }

#         try:
#             # Gemini API endpoint with API key
#             url = f"{self.base_url}{self.model}:generateContent?key={self.api_key}"
            
#             headers = {
#                 "Content-Type": "application/json"
#             }

#             # Convert OpenAI-style messages to Gemini format
#             contents = []
#             for msg in messages:
#                 role = "user" if msg["role"] == "user" else "model"
#                 contents.append({
#                     "role": role,
#                     "parts": [{"text": msg["content"]}]
#                 })

#             data = {
#                 "contents": contents,
#                 "generationConfig": {
#                     "maxOutputTokens": LLM_CONFIG['max_tokens'],
#                     "temperature": LLM_CONFIG['temperature']
#                 }
#             }

#             response = requests.post(url, headers=headers, json=data, timeout=30)
#             response.raise_for_status()
            
#             # Convert Gemini response format to OpenAI format for compatibility
#             gemini_response = response.json()
            
#             # Extract the text from Gemini's response structure
#             if "candidates" in gemini_response and len(gemini_response["candidates"]) > 0:
#                 content = gemini_response["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
#                 # Return in OpenAI-compatible format
#                 return {
#                     "choices": [{
#                         "message": {
#                             "content": content
#                         }
#                     }]
#                 }
#             else:
#                 # If response doesn't have expected structure, return fallback
#                 raise ValueError("Unexpected Gemini API response format")
#         except requests.exceptions.RequestException as e:
#             # Try to extract status code if available
#             status_code = None
#             if hasattr(e, 'response') and getattr(e, 'response') is not None:
#                 status_code = getattr(e, 'response').status_code

#             # Log debug message (use debug so it doesn't clutter terminal by default)
#             logger.debug("Gemini API Error (%s): %s", status_code, e)

#             # If payment required or auth error, switch to mock/fallback
#             if status_code in [402, 401, 403]:
#                 logger.debug("Gemini API returned error %s. Switching to fallback/mock LLM. Check API key in config.py", status_code)
#                 self.use_mock_service = True

#             # Return fallback response
#             return {
#                 "choices": [{
#                     "message": {
#                         "content": json.dumps(self._get_fallback_response(messages))
#                     }
#                 }]
#             }

#     def _get_fallback_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
#         """Get fallback response when API is unavailable"""
#         user_content = messages[-1].get('content', '').lower()

#         if 'analyze this service request and determine the best search strategy' in user_content:
#             import re
#             match = re.search(r'"([^"]+)"', user_content)
#             user_query = match.group(1) if match else "general service"
#             search_match = re.search(r'search preference: (\w+)', user_content)
#             search_preference = search_match.group(1) if search_match else "both"
#             return self._fallback_analysis(user_query, search_preference)

#         elif 'analyze these search results from distributed databases' in user_content:
#             return {
#                 "best_overall_choice": "both",
#                 "recommendation_reasoning": "Both companies and individuals offer good value for this service type.",
#                 "advantages_companies": ["Professional warranty", "Insurance coverage", "Multiple workers"],
#                 "advantages_individuals": ["Competitive pricing", "Personal service", "Flexible scheduling"],
#                 "price_comparison": "similar",
#                 "quality_assessment": "similar",
#                 "recommended_top_3": [],
#                 "confidence_score": 0.75
#             }

#         else:
#             return {
#                 "recommended_type": "both",
#                 "confidence": 0.7,
#                 "reasoning": "Both options are suitable for this request.",
#                 "key_factors": ["Rating", "Experience", "Availability"],
#                 "alternative_suggestion": "Compare specific providers from both categories"
#             }

#     def analyze_distributed_service_request(self, user_query: str, search_preference: str = 'both') -> Dict[str, Any]:
#         """Analyze user's service request for distributed database search"""
#         prompt = f"""
#         Analyze this service request and determine the best search strategy across distributed databases:

#         User Query: "{user_query}"
#         Search Preference: {search_preference}

#         The system has two types of providers:
#         1. Companies (Primary Database) - Professional service companies with multiple workers
#         2. Individual Workers (Secondary Database) - Self-employed professionals and freelancers

#         Provide analysis in JSON format:
#         {{
#             "service_type": "plumbing/electrical/carpentry/painting/automotive/hvac/cleaning/landscaping/security/other",
#             "urgency": "low/medium/high/emergency",
#             "description": "brief description of the issue",
#             "keywords": ["keyword1", "keyword2"],
#             "estimated_complexity": "simple/moderate/complex",
#             "location_preference": "if mentioned",
#             "recommended_provider_type": "company/individual/both",
#             "reasoning": "Why this provider type is recommended",
#             "search_scope": "primary/secondary/both",
#             "confidence_score": 0.85
#         }}
#         """

#         messages = [
#             {"role": "system", "content": "You are a distributed service request analyzer. Determine the best provider type and search strategy. Respond in valid JSON format only."},
#             {"role": "user", "content": prompt}
#         ]

#         response = self._make_api_request(messages)

#         try:
#             content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
#             json_match = re.search(r'\{.*\}', content, re.DOTALL)
#             if json_match:
#                 return json.loads(json_match.group())
#         except json.JSONDecodeError:
#             logger.debug("Failed to parse LLM response as JSON")

#         return self._fallback_analysis(user_query, search_preference)

#     def _fallback_analysis(self, user_query: str, search_preference: str) -> Dict[str, Any]:
#         """Fallback analysis when LLM is not available"""
#         user_query_lower = user_query.lower()

#         # Service type detection
#         service_type = "other"
#         if any(word in user_query_lower for word in ['plumb', 'pipe', 'leak', 'faucet', 'drain']):
#             service_type = "plumbing"
#         elif any(word in user_query_lower for word in ['electric', 'wire', 'outlet', 'switch', 'circuit']):
#             service_type = "electrical"
#         elif any(word in user_query_lower for word in ['carpent', 'wood', 'furniture', 'cabinet']):
#             service_type = "carpentry"
#         elif any(word in user_query_lower for word in ['paint', 'wall', 'color']):
#             service_type = "painting"
#         elif any(word in user_query_lower for word in ['car', 'auto', 'vehicle', 'engine']):
#             service_type = "automotive"
#         elif any(word in user_query_lower for word in ['ac', 'air condition', 'cooling']):
#             service_type = "hvac"
#         elif any(word in user_query_lower for word in ['clean', 'maid', 'janitor']):
#             service_type = "cleaning"
#         elif any(word in user_query_lower for word in ['garden', 'lawn', 'landscape']):
#             service_type = "landscaping"

#         # Urgency detection
#         urgency = "medium"
#         if any(word in user_query_lower for word in ['emergency', 'urgent', 'asap', 'immediate']):
#             urgency = "high" if 'emergency' in user_query_lower else "high"
#         elif any(word in user_query_lower for word in ['when possible', 'soon', 'next week']):
#             urgency = "medium"
#         elif any(word in user_query_lower for word in ['no rush', 'when convenient']):
#             urgency = "low"

#         # Provider type recommendation
#         recommended_provider_type = "both"
#         reasoning = "Both companies and individual workers can handle this request"

#         if any(word in user_query_lower for word in ['large', 'major', 'commercial', 'business', 'office']):
#             recommended_provider_type = "company"
#             reasoning = "Large-scale projects are better handled by professional companies"
#         elif any(word in user_query_lower for word in ['small', 'minor', 'quick', 'simple']):
#             recommended_provider_type = "individual"
#             reasoning = "Small jobs are well-suited for individual workers"
#         elif any(word in user_query_lower for word in ['emergency', 'urgent', 'asap']):
#             recommended_provider_type = "individual"
#             reasoning = "Individual workers often have faster response times for emergencies"
#         elif any(word in user_query_lower for word in ['warranty', 'insurance', 'certified', 'licensed']):
#             recommended_provider_type = "company"
#             reasoning = "Companies provide better warranty and insurance coverage"

#         # Search scope determination
#         search_scope = search_preference
#         if search_preference == "both":
#             search_scope = "both"
#         elif search_preference == "primary" and recommended_provider_type == "company":
#             search_scope = "primary"
#         elif search_preference == "secondary" and recommended_provider_type == "individual":
#             search_scope = "secondary"

#         return {
#             "service_type": service_type,
#             "urgency": urgency,
#             "description": user_query,
#             "keywords": [service_type] if service_type != "other" else [],
#             "estimated_complexity": "moderate",
#             "location_preference": "",
#             "recommended_provider_type": recommended_provider_type,
#             "reasoning": reasoning,
#             "search_scope": search_scope,
#             "confidence_score": 0.75
#         }

#     def analyze_cross_database_results(self, companies: List[Dict], employees: List[Dict], user_query: str) -> Dict[str, Any]:
#         """Analyze and compare results from both databases"""
#         prompt = f"""
#         Analyze these search results from distributed databases and provide intelligent recommendations:

#         User Query: "{user_query}"

#         Companies Found: {len(companies)}
#         Individual Workers Found: {len(employees)}

#         Company Results:
#         {json.dumps(companies[:3], indent=2)}

#         Individual Worker Results:
#         {json.dumps(employees[:3], indent=2)}

#         Provide analysis in JSON format:
#         {{
#             "best_overall_choice": "company/individual/specific",
#             "recommendation_reasoning": "Detailed explanation of recommendations",
#             "advantages_companies": ["advantage1", "advantage2"],
#             "advantages_individuals": ["advantage1", "advantage2"],
#             "price_comparison": "companies_higher/companies_lower/similar",
#             "quality_assessment": "companies_better/individuals_better/similar",
#             "recommended_top_3": [
#                 {{
#                     "id": 1,
#                     "name": "Provider Name",
#                     "type": "company/individual",
#                     "reason": "Why this is recommended"
#                 }}
#             ],
#             "confidence_score": 0.85
#         }}
#         """

#         messages = [
#             {"role": "system", "content": "You are a distributed service comparison expert. Analyze both company and individual worker options. Respond in valid JSON format only."},
#             {"role": "user", "content": prompt}
#         ]

#         response = self._make_api_request(messages)

#         try:
#             content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
#             json_match = re.search(r'\{.*\}', content, re.DOTALL)
#             if json_match:
#                 return json.loads(json_match.group())
#         except json.JSONDecodeError:
#             print("Failed to parse LLM cross-database analysis")

#         return self._fallback_cross_analysis(companies, employees, user_query)

#     def _fallback_cross_analysis(self, companies: List[Dict], employees: List[Dict], user_query: str) -> Dict[str, Any]:
#         """Fallback cross-database analysis"""
#         # Simple logic for comparison
#         top_recommendations = []

#         # Add top companies
#         for company in companies[:2]:
#             top_recommendations.append({
#                 "id": company['id'],
#                 "name": company['name'],
#                 "type": "company",
#                 "reason": f"High rating ({company['rating']}) with {company['total_reviews']} reviews"
#             })

#         # Add top employees
#         for employee in employees[:1]:
#             top_recommendations.append({
#                 "id": employee['id'],
#                 "name": employee['name'],
#                 "type": "individual",
#                 "reason": f"Experienced ({employee['experience_years']} years) with excellent rating ({employee['rating']})"
#             })

#         # Determine advantages
#         advantages_companies = ["Professional insurance", "Multiple workers", "Warranty coverage"]
#         advantages_individuals = ["Personal attention", "Often lower cost", "Flexible scheduling"]

#         # Price comparison (simple heuristic)
#         avg_company_cost = sum(c.get('avg_cost', 100) for c in companies) / len(companies) if companies else 100
#         avg_employee_cost = sum(e.get('avg_cost', 80) for e in employees) / len(employees) if employees else 80

#         price_comparison = "companies_lower" if avg_company_cost < avg_employee_cost else "individuals_lower"

#         return {
#             "best_overall_choice": "both",
#             "recommendation_reasoning": "Both companies and individual workers offer good options. Companies provide reliability while individuals offer competitive pricing.",
#             "advantages_companies": advantages_companies,
#             "advantages_individuals": advantages_individuals,
#             "price_comparison": price_comparison,
#             "quality_assessment": "similar",
#             "recommended_top_3": top_recommendations[:3],
#             "confidence_score": 0.70
#         }

#     def generate_intelligent_summary(self, user_query: str, search_results: Dict) -> str:
#         """Generate intelligent summary of search results"""
#         companies_count = search_results.get('companies_count', 0)
#         employees_count = search_results.get('employees_count', 0)
#         total_count = search_results.get('total_count', 0)

#         if total_count == 0:
#             return "No service providers found matching your request. Try adjusting your search criteria."

#         summary = f"Found {total_count} service providers matching your request: "

#         if companies_count > 0 and employees_count > 0:
#             summary += f"{companies_count} professional companies and {employees_count} individual workers."
#         elif companies_count > 0:
#             summary += f"{companies_count} professional companies available."
#         else:
#             summary += f"{employees_count} individual workers available."

#         # Add insights based on the query
#         user_query_lower = user_query.lower()
#         if any(word in user_query_lower for word in ['emergency', 'urgent', 'asap']):
#             summary += " For urgent requests, consider individual workers for faster response times."
#         elif any(word in user_query_lower for word in ['large', 'major', 'commercial']):
#             summary += " For large projects, companies may offer better resources and project management."
#         elif any(word in user_query_lower for word in ['warranty', 'insurance']):
#             summary += " Companies typically provide better warranty and insurance coverage."

#         return summary

#     def suggest_provider_type(self, user_query: str, user_preferences: Dict = None) -> Dict[str, Any]:
#         """Suggest whether user should choose company or individual worker"""
#         prompt = f"""
#         Based on this service request and user preferences, recommend the best provider type:

#         User Query: "{user_query}"
#         User Preferences: {json.dumps(user_preferences or {})}

#         Consider factors like:
#         - Project size and complexity
#         - Urgency
#         - Budget considerations
#         - Need for warranty/insurance
#         - Preference for personal vs professional service

#         Provide recommendation in JSON format:
#         {{
#             "recommended_type": "company/individual/both",
#             "confidence": 0.85,
#             "reasoning": "Detailed explanation",
#             "key_factors": ["factor1", "factor2"],
#             "alternative_suggestion": "If first choice not available"
#         }}
#         """

#         messages = [
#             {"role": "system", "content": "You are a service selection advisor. Consider all factors to recommend the best provider type. Respond in valid JSON format only."},
#             {"role": "user", "content": prompt}
#         ]

#         response = self._make_api_request(messages)

#         try:
#             content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
#             json_match = re.search(r'\{.*\}', content, re.DOTALL)
#             if json_match:
#                 return json.loads(json_match.group())
#         except json.JSONDecodeError:
#             pass

#         return {
#             "recommended_type": "both",
#             "confidence": 0.6,
#             "reasoning": "Both companies and individual workers can handle this request effectively.",
#             "key_factors": ["Service availability", "Rating", "Experience"],
#             "alternative_suggestion": "Consider both options and compare specific providers"
#         }


# # Mock service for testing without API key
# class MockDistributedLLMService(DistributedLLMService):
#     def _make_api_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
#         """Mock API request for distributed system testing"""
#         user_content = messages[-1].get('content', '').lower()

#         if 'analyze this service request and determine the best search strategy' in user_content:
#             # Extract user query
#             import re
#             match = re.search(r'"([^"]+)"', user_content)
#             user_query = match.group(1) if match else "general service"

#             # Extract search preference
#             search_match = re.search(r'search preference: (\w+)', user_content)
#             search_preference = search_match.group(1) if search_match else "both"

#             return {
#                 "choices": [{
#                     "message": {
#                         "content": json.dumps(self._fallback_analysis(user_query, search_preference))
#                     }
#                 }]
#             }

#         elif 'analyze these search results from distributed databases' in user_content:
#             return {
#                 "choices": [{
#                     "message": {
#                         "content": json.dumps({
#                             "best_overall_choice": "both",
#                             "recommendation_reasoning": "Both companies and individuals offer good value for this service type.",
#                             "advantages_companies": ["Professional warranty", "Insurance coverage", "Multiple workers"],
#                             "advantages_individuals": ["Competitive pricing", "Personal service", "Flexible scheduling"],
#                             "price_comparison": "similar",
#                             "quality_assessment": "similar",
#                             "recommended_top_3": [],
#                             "confidence_score": 0.75
#                         })
#                     }
#                 }]
#             }

#         else:
#             return {
#                 "choices": [{
#                     "message": {
#                         "content": json.dumps({
#                             "recommended_type": "both",
#                             "confidence": 0.7,
#                             "reasoning": "Both options are suitable for this request.",
#                             "key_factors": ["Rating", "Experience", "Availability"],
#                             "alternative_suggestion": "Compare specific providers from both categories"
#                         })
#                     }
#                 }]
#             }


import json
import re
import logging
from typing import Any, Dict, List

from google import genai  

from config import LLM_CONFIG, SERVICE_SORTING_WEIGHTS, SERVICE_TYPES  # keep as before

logger = logging.getLogger(__name__)


class DistributedLLMService:
    def __init__(self):
        self.api_key = LLM_CONFIG.get('api_key')
        self.model = LLM_CONFIG.get('model', 'gemini-2.0-flash-001')
        self.use_mock_service = False  # if True, we short-circuit to fallbacks

        # GenAI client (Gemini Developer API or Vertex depending on env/config)
        self.client = None
        try:
            if self.api_key:
                # Explicit API key path
                self.client = genai.Client(api_key=self.api_key)
            else:
                # Fall back to env vars (GEMINI_API_KEY / Vertex env)
                self.client = genai.Client()
        except Exception as e:
            logger.debug("Failed to create GenAI client, using fallback LLM: %s", e)
            self.client = None
            self.use_mock_service = True

    def _make_api_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Make API request to Gemini via google-genai and wrap result
        in an OpenAI-style `choices[0].message.content` dict.
        """
        # If configured to use the mock service or no client is available, return fallback immediately
        if self.use_mock_service or self.client is None:
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps(self._get_fallback_response(messages))
                    }
                }]
            }

        try:
            # Flatten messages into a single prompt string while preserving system hints
            # so your downstream JSON parsing logic still works.
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"User: {content}")
                else:
                    prompt_parts.append(content)

            prompt = "\n\n".join(prompt_parts).strip()

            # Call Gemini via GenAI SDK
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                generation_config={
                    "temperature": LLM_CONFIG.get("temperature", 0.3),
                    "max_output_tokens": LLM_CONFIG.get("max_tokens", 1024),
                },
            )

            text = getattr(response, "text", "") or ""

            # Wrap Gemini text result to look like OpenAI-style response
            return {
                "choices": [{
                    "message": {
                        "content": text
                    }
                }]
            }

        except Exception as e:
            # Any SDK/network error → log and fall back
            logger.debug("GenAI SDK error, switching to fallback/mock LLM: %s", e)
            self.use_mock_service = True
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps(self._get_fallback_response(messages))
                    }
                }]
            }

    def _get_fallback_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Get fallback response when API is unavailable"""
        user_content = messages[-1].get('content', '').lower()

        if 'analyze this service request and determine the best search strategy' in user_content:
            import re
            match = re.search(r'"([^"]+)"', user_content)
            user_query = match.group(1) if match else "general service"
            search_match = re.search(r'search preference: (\w+)', user_content)
            search_preference = search_match.group(1) if search_match else "both"
            return self._fallback_analysis(user_query, search_preference)

        elif 'analyze these search results from distributed databases' in user_content:
            return {
                "best_overall_choice": "both",
                "recommendation_reasoning": "Both companies and individuals offer good value for this service type.",
                "advantages_companies": ["Professional warranty", "Insurance coverage", "Multiple workers"],
                "advantages_individuals": ["Competitive pricing", "Personal service", "Flexible scheduling"],
                "price_comparison": "similar",
                "quality_assessment": "similar",
                "recommended_top_3": [],
                "confidence_score": 0.75
            }

        else:
            return {
                "recommended_type": "both",
                "confidence": 0.7,
                "reasoning": "Both options are suitable for this request.",
                "key_factors": ["Rating", "Experience", "Availability"],
                "alternative_suggestion": "Compare specific providers from both categories"
            }

    def analyze_distributed_service_request(self, user_query: str, search_preference: str = 'both') -> Dict[str, Any]:
        """Analyze user's service request for distributed database search"""
        prompt = f"""
        Analyze this service request and determine the best search strategy across distributed databases:

        User Query: "{user_query}"
        Search Preference: {search_preference}

        The system has two types of providers:
        1. Companies (Primary Database) - Professional service companies with multiple workers
        2. Individual Workers (Secondary Database) - Self-employed professionals and freelancers

        Provide analysis in JSON format:
        {{
            "service_type": "plumbing/electrical/carpentry/painting/automotive/hvac/cleaning/landscaping/security/other",
            "urgency": "low/medium/high/emergency",
            "description": "brief description of the issue",
            "keywords": ["keyword1", "keyword2"],
            "estimated_complexity": "simple/moderate/complex",
            "location_preference": "if mentioned",
            "recommended_provider_type": "company/individual/both",
            "reasoning": "Why this provider type is recommended",
            "search_scope": "primary/secondary/both",
            "confidence_score": 0.85
        }}
        """

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a distributed service request analyzer. "
                    "Determine the best provider type and search strategy. "
                    "Respond in valid JSON format only."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response = self._make_api_request(messages)

        try:
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            logger.debug("Failed to parse LLM response as JSON")

        return self._fallback_analysis(user_query, search_preference)

    def _fallback_analysis(self, user_query: str, search_preference: str) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        user_query_lower = user_query.lower()

        # Service type detection
        service_type = "other"
        if any(word in user_query_lower for word in ['plumb', 'pipe', 'leak', 'faucet', 'drain']):
            service_type = "plumbing"
        elif any(word in user_query_lower for word in ['electric', 'wire', 'outlet', 'switch', 'circuit']):
            service_type = "electrical"
        elif any(word in user_query_lower for word in ['carpent', 'wood', 'furniture', 'cabinet']):
            service_type = "carpentry"
        elif any(word in user_query_lower for word in ['paint', 'wall', 'color']):
            service_type = "painting"
        elif any(word in user_query_lower for word in ['car', 'auto', 'vehicle', 'engine']):
            service_type = "automotive"
        elif any(word in user_query_lower for word in ['ac', 'air condition', 'cooling']):
            service_type = "hvac"
        elif any(word in user_query_lower for word in ['clean', 'maid', 'janitor']):
            service_type = "cleaning"
        elif any(word in user_query_lower for word in ['garden', 'lawn', 'landscape']):
            service_type = "landscaping"

        # Urgency detection
        urgency = "medium"
        if any(word in user_query_lower for word in ['emergency', 'urgent', 'asap', 'immediate']):
            urgency = "high"
        elif any(word in user_query_lower for word in ['when possible', 'soon', 'next week']):
            urgency = "medium"
        elif any(word in user_query_lower for word in ['no rush', 'when convenient']):
            urgency = "low"

        # Provider type recommendation
        recommended_provider_type = "both"
        reasoning = "Both companies and individual workers can handle this request"

        if any(word in user_query_lower for word in ['large', 'major', 'commercial', 'business', 'office']):
            recommended_provider_type = "company"
            reasoning = "Large-scale projects are better handled by professional companies"
        elif any(word in user_query_lower for word in ['small', 'minor', 'quick', 'simple']):
            recommended_provider_type = "individual"
            reasoning = "Small jobs are well-suited for individual workers"
        elif any(word in user_query_lower for word in ['emergency', 'urgent', 'asap']):
            recommended_provider_type = "individual"
            reasoning = "Individual workers often have faster response times for emergencies"
        elif any(word in user_query_lower for word in ['warranty', 'insurance', 'certified', 'licensed']):
            recommended_provider_type = "company"
            reasoning = "Companies provide better warranty and insurance coverage"

        # Search scope determination
        search_scope = search_preference
        if search_preference == "both":
            search_scope = "both"
        elif search_preference == "primary" and recommended_provider_type == "company":
            search_scope = "primary"
        elif search_preference == "secondary" and recommended_provider_type == "individual":
            search_scope = "secondary"

        return {
            "service_type": service_type,
            "urgency": urgency,
            "description": user_query,
            "keywords": [service_type] if service_type != "other" else [],
            "estimated_complexity": "moderate",
            "location_preference": "",
            "recommended_provider_type": recommended_provider_type,
            "reasoning": reasoning,
            "search_scope": search_scope,
            "confidence_score": 0.75,
        }

    def analyze_cross_database_results(self, companies: List[Dict], employees: List[Dict], user_query: str) -> Dict[str, Any]:
        """Analyze and compare results from both databases"""
        prompt = f"""
        Analyze these search results from distributed databases and provide intelligent recommendations:

        User Query: "{user_query}"

        Companies Found: {len(companies)}
        Individual Workers Found: {len(employees)}

        Company Results:
        {json.dumps(companies[:3], indent=2)}

        Individual Worker Results:
        {json.dumps(employees[:3], indent=2)}

        Provide analysis in JSON format:
        {{
            "best_overall_choice": "company/individual/specific",
            "recommendation_reasoning": "Detailed explanation of recommendations",
            "advantages_companies": ["advantage1", "advantage2"],
            "advantages_individuals": ["advantage1", "advantage2"],
            "price_comparison": "companies_higher/companies_lower/similar",
            "quality_assessment": "companies_better/individuals_better/similar",
            "recommended_top_3": [
                {{
                    "id": 1,
                    "name": "Provider Name",
                    "type": "company/individual",
                    "reason": "Why this is recommended"
                }}
            ],
            "confidence_score": 0.85
        }}
        """

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a distributed service comparison expert. "
                    "Analyze both company and individual worker options. "
                    "Respond in valid JSON format only."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response = self._make_api_request(messages)

        try:
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            logger.debug("Failed to parse LLM cross-database analysis")

        return self._fallback_cross_analysis(companies, employees, user_query)

    def _fallback_cross_analysis(self, companies: List[Dict], employees: List[Dict], user_query: str) -> Dict[str, Any]:
        """Fallback cross-database analysis"""
        top_recommendations = []

        # Add top companies
        for company in companies[:2]:
            top_recommendations.append({
                "id": company.get('id') or company.get('company_id'),
                "name": company.get('name') or company.get('company_name'),
                "type": "company",
                "reason": f"High rating ({company.get('rating')}) with {company.get('total_reviews')} reviews",
            })

        # Add top employees
        for employee in employees[:1]:
            top_recommendations.append({
                "id": employee.get('id') or employee.get('employee_id'),
                "name": employee.get('name'),
                "type": "individual",
                "reason": f"Experienced ({employee.get('experience_years')} years) with excellent rating ({employee.get('rating')})",
            })

        advantages_companies = ["Professional insurance", "Multiple workers", "Warranty coverage"]
        advantages_individuals = ["Personal attention", "Often lower cost", "Flexible scheduling"]

        # Price comparison (simple heuristic)
        avg_company_cost = (
            sum(c.get('avg_cost', 100) for c in companies) / len(companies)
            if companies else 100
        )
        avg_employee_cost = (
            sum(e.get('avg_cost', 80) for e in employees) / len(employees)
            if employees else 80
        )

        price_comparison = "companies_lower" if avg_company_cost < avg_employee_cost else "individuals_lower"

        return {
            "best_overall_choice": "both",
            "recommendation_reasoning": (
                "Both companies and individual workers offer good options. "
                "Companies provide reliability while individuals offer competitive pricing."
            ),
            "advantages_companies": advantages_companies,
            "advantages_individuals": advantages_individuals,
            "price_comparison": price_comparison,
            "quality_assessment": "similar",
            "recommended_top_3": top_recommendations[:3],
            "confidence_score": 0.70,
        }

    def generate_intelligent_summary(self, user_query: str, search_results: Dict) -> str:
        """Generate intelligent summary of search results"""
        companies_count = search_results.get('companies_count', 0)
        employees_count = search_results.get('employees_count', 0)
        total_count = search_results.get('total_count', 0)

        if total_count == 0:
            return "No service providers found matching your request. Try adjusting your search criteria."

        summary = f"Found {total_count} service providers matching your request: "

        if companies_count > 0 and employees_count > 0:
            summary += f"{companies_count} professional companies and {employees_count} individual workers."
        elif companies_count > 0:
            summary += f"{companies_count} professional companies available."
        else:
            summary += f"{employees_count} individual workers available."

        user_query_lower = user_query.lower()
        if any(word in user_query_lower for word in ['emergency', 'urgent', 'asap']):
            summary += " For urgent requests, consider individual workers for faster response times."
        elif any(word in user_query_lower for word in ['large', 'major', 'commercial']):
            summary += " For large projects, companies may offer better resources and project management."
        elif any(word in user_query_lower for word in ['warranty', 'insurance']):
            summary += " Companies typically provide better warranty and insurance coverage."

        return summary

    def suggest_provider_type(self, user_query: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """Suggest whether user should choose company or individual worker"""
        prompt = f"""
        Based on this service request and user preferences, recommend the best provider type:

        User Query: "{user_query}"
        User Preferences: {json.dumps(user_preferences or {})}

        Consider factors like:
        - Project size and complexity
        - Urgency
        - Budget considerations
        - Need for warranty/insurance
        - Preference for personal vs professional service

        Provide recommendation in JSON format:
        {{
            "recommended_type": "company/individual/both",
            "confidence": 0.85,
            "reasoning": "Detailed explanation",
            "key_factors": ["factor1", "factor2"],
            "alternative_suggestion": "If first choice not available"
        }}
        """

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a service selection advisor. "
                    "Consider all factors to recommend the best provider type. "
                    "Respond in valid JSON format only."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response = self._make_api_request(messages)

        try:
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        return {
            "recommended_type": "both",
            "confidence": 0.6,
            "reasoning": "Both companies and individual workers can handle this request effectively.",
            "key_factors": ["Service availability", "Rating", "Experience"],
            "alternative_suggestion": "Consider both options and compare specific providers",
        }


# Mock service for testing without API key
class MockDistributedLLMService(DistributedLLMService):
    def _make_api_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Mock API request for distributed system testing"""
        user_content = messages[-1].get('content', '').lower()

        if 'analyze this service request and determine the best search strategy' in user_content:
            import re
            match = re.search(r'"([^"]+)"', user_content)
            user_query = match.group(1) if match else "general service"
            search_match = re.search(r'search preference: (\w+)', user_content)
            search_preference = search_match.group(1) if search_match else "both"

            return {
                "choices": [{
                    "message": {
                        "content": json.dumps(self._fallback_analysis(user_query, search_preference))
                    }
                }]
            }

        elif 'analyze these search results from distributed databases' in user_content:
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "best_overall_choice": "both",
                            "recommendation_reasoning": "Both companies and individuals offer good value for this service type.",
                            "advantages_companies": ["Professional warranty", "Insurance coverage", "Multiple workers"],
                            "advantages_individuals": ["Competitive pricing", "Personal service", "Flexible scheduling"],
                            "price_comparison": "similar",
                            "quality_assessment": "similar",
                            "recommended_top_3": [],
                            "confidence_score": 0.75,
                        })
                    }
                }]
            }

        else:
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "recommended_type": "both",
                            "confidence": 0.7,
                            "reasoning": "Both options are suitable for this request.",
                            "key_factors": ["Rating", "Experience", "Availability"],
                            "alternative_suggestion": "Compare specific providers from both categories",
                        })
                    }
                }]
            }
