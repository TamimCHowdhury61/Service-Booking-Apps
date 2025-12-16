from typing import Dict, List, Any
from distributed_database_manager import DistributedDatabaseManager
from distributed_llm_service import DistributedLLMService
from query_federation_engine import QueryFederationEngine, PromptRewriteEngine, ResearchCatalog


class DistributedSortingService:
    def __init__(self, db_manager: DistributedDatabaseManager):
        self.db_manager = db_manager
        self.llm_service = DistributedLLMService()

        # Initialize advanced query federation features
        self.query_federation_engine = QueryFederationEngine(db_manager, self, self.llm_service)
        self.prompt_rewriter = PromptRewriteEngine()
        self.research_catalog = ResearchCatalog()

    def get_intelligent_recommendations(self, user_query: str, search_preference: str = 'both', limit: int = 20) -> Dict[str, Any]:
        """Get intelligent recommendations from distributed databases"""
        # Analyze the user's request
        analysis = self.llm_service.analyze_distributed_service_request(user_query, search_preference)

        # Determine search scope
        search_scope = analysis.get('search_scope', 'both')
        service_type = analysis.get('service_type', '')
        location = analysis.get('location_preference', '')

        print(f"Searching for: {service_type}")
        print(f"Search scope: {search_scope}")
        print(f"Recommended provider type: {analysis.get('recommended_provider_type')}")

        # Get cross-laptop results
        search_results = self.db_manager.get_cross_laptop_results(service_type, location)

        # Filter results based on search scope
        if search_scope == 'primary':
            search_results['combined_results'] = [r for r in search_results['combined_results'] if r['data_source'] == 'Primary']
        elif search_scope == 'secondary':
            search_results['combined_results'] = [r for r in search_results['combined_results'] if r['data_source'] == 'Secondary']

        # Apply intelligent sorting
        sorted_results = self._apply_intelligent_sorting(search_results['combined_results'], analysis)

        # Get cross-database analysis
        cross_analysis = self.llm_service.analyze_cross_database_results(
            search_results['companies'],
            search_results['employees'],
            user_query
        )

        # Generate intelligent summary
        summary = self.llm_service.generate_intelligent_summary(user_query, search_results)

        return {
            'employees': sorted_results[:limit],
            'analysis': analysis,
            'search_scope': search_scope,
            'primary_count': len(search_results['companies']),
            'secondary_count': len(search_results['employees']),
            'total_available': len(search_results['combined_results']),
            'cross_analysis': cross_analysis,
            'summary': summary,
            'quality_analysis': cross_analysis,
            'alternatives': self._get_alternative_suggestions(service_type, analysis)
        }

    def _apply_intelligent_sorting(self, results: List[Dict], analysis: Dict) -> List[Dict]:
        """Apply intelligent sorting based on analysis and preferences"""
        if not results:
            return results

        # Scoring weights based on user preferences
        urgency = analysis.get('urgency', 'medium')
        complexity = analysis.get('estimated_complexity', 'moderate')
        recommended_type = analysis.get('recommended_provider_type', 'both')

        for result in results:
            score = 0.0
            factors = {}

            # Base rating score (40% weight)
            rating = result.get('rating', 0)
            # Convert Decimal to float for calculations
            rating_float = float(rating) if isinstance(rating, (int, float, str)) else 0.0
            score += (rating_float / 5.0) * 40
            factors['rating'] = (rating_float / 5.0) * 40

            # Provider type preference (20% weight)
            if recommended_type == 'company' and result['type'] == 'Company':
                score += 20
            elif recommended_type == 'individual' and result['type'] == 'Individual Worker':
                score += 20
            else:
                score += 10  # Neutral score
            factors['provider_type_match'] = score - factors.get('rating', 0)

            # Urgency consideration (15% weight)
            if urgency == 'high' or urgency == 'emergency':
                if result.get('emergency_service', False):
                    score += 15
                else:
                    # For urgent requests, prioritize faster response times
                    response_time = result.get('avg_response_time_hours', 24)
                    if response_time <= 2:
                        score += 12
                    elif response_time <= 6:
                        score += 8
                    elif response_time <= 12:
                        score += 4
            elif urgency == 'medium':
                response_time = result.get('avg_response_time_hours', 24)
                if response_time <= 6:
                    score += 10
                elif response_time <= 12:
                    score += 6
            factors['urgency_score'] = score - sum(factors.values())

            # Experience/Reviews consideration (15% weight)
            if result['type'] == 'Company':
                total_reviews = result.get('total_reviews', 0)
                if total_reviews >= 100:
                    score += 15
                elif total_reviews >= 50:
                    score += 10
                elif total_reviews >= 20:
                    score += 5
            else:  # Individual Worker
                experience = result.get('experience_years', 0)
                total_orders = result.get('total_orders', 0)
                if experience >= 10 and total_orders >= 100:
                    score += 15
                elif experience >= 5 and total_orders >= 50:
                    score += 10
                elif experience >= 2 and total_orders >= 20:
                    score += 5
            factors['experience_score'] = score - sum(factors.values())

            # Certification level consideration (10% weight)
            if result['type'] == 'Individual Worker':
                cert_level = result.get('certification_level', 'None')
                if cert_level == 'Master':
                    score += 10
                elif cert_level == 'Professional':
                    score += 8
                elif cert_level == 'Basic':
                    score += 5
            else:  # Company
                # Companies get base score for being established
                score += 6
            factors['certification_score'] = score - sum(factors.values())

            result['comprehensive_score'] = score
            result['scoring_factors'] = factors

        # Sort by comprehensive score (descending)
        results.sort(key=lambda x: x.get('comprehensive_score', 0), reverse=True)

        return results

    def _get_alternative_suggestions(self, service_type: str, analysis: Dict) -> List[str]:
        """Get alternative service suggestions"""
        alternatives = []

        service_mapping = {
            'plumbing': ['HVAC services', 'General handyman', 'Pipe inspection services'],
            'electrical': ['Generator services', 'Home automation', 'Safety inspection services'],
            'carpentry': ['Furniture repair', 'Custom shelving', 'Kitchen remodeling'],
            'painting': ['Wallpaper installation', 'Pressure washing', 'Interior decorating'],
            'automotive': ['Car detailing', 'Tire services', 'Oil change services'],
            'hvac': ['Insulation services', 'Duct cleaning', 'Thermostat installation'],
            'cleaning': ['Organizational services', 'Disinfection services', 'Window cleaning'],
            'landscaping': ['Tree removal', 'Irrigation installation', 'Hardscaping']
        }

        if service_type in service_mapping:
            alternatives = service_mapping[service_type][:3]
        else:
            alternatives = ['General handyman', 'Home maintenance', 'Property inspection']

        return alternatives

    def get_provider_recommendations(self, provider_type: str, service_type: str = '', limit: int = 10) -> List[Dict]:
        """Get specific recommendations for provider type"""
        if provider_type == 'company':
            # Search only in primary database
            companies = self.db_manager.search_companies(service_type)
            results = []
            for company in companies:
                results.append({
                    'id': company['company_id'],
                    'name': company['company_name'],
                    'type': 'Company',
                    'rating': company['rating'],
                    'description': company['description'],
                    'service_regions': company['service_regions'],
                    'avg_cost': company['avg_hourly_rate'],
                    'specialization': company['specialization_areas'],
                    'data_source': 'Primary',
                    'total_reviews': company['total_reviews'],
                    'phone': company['phone'],
                    'email': company['email'],
                    'website': company['website']
                })
        else:
            # Search only in secondary database
            employees = self.db_manager.search_employees(service_type)
            results = []
            for employee in employees:
                results.append({
                    'id': employee['employee_id'],
                    'name': employee['name'],
                    'type': 'Individual Worker',
                    'rating': employee['rating'],
                    'description': employee.get('bio', ''),
                    'service_regions': employee['preferred_regions'],
                    'avg_cost': employee['avg_cost_per_hour'],
                    'specialization': employee['specialization'],
                    'data_source': 'Secondary',
                    'experience_years': employee['experience_years'],
                    'total_orders': employee['total_completed_orders'],
                    'phone': employee['phone'],
                    'email': employee['email'],
                    'certification_level': employee['certification_level'],
                    'emergency_service': employee['emergency_service']
                })

        # Apply basic sorting
        results.sort(key=lambda x: x.get('rating', 0), reverse=True)

        return results[:limit]

    def compare_providers(self, provider_ids: List[tuple]) -> Dict[str, Any]:
        """Compare specific providers (id, type tuples)"""
        providers = []

        for provider_id, provider_type in provider_ids:
            if provider_type == 'company':
                details = self.db_manager.get_company_details(provider_id)
                if details:
                    providers.append({
                        'id': provider_id,
                        'type': 'Company',
                        'details': details
                    })
            else:  # employee
                details = self.db_manager.get_employee_details(provider_id)
                if details:
                    providers.append({
                        'id': provider_id,
                        'type': 'Individual Worker',
                        'details': details
                    })

        # Generate comparison analysis
        comparison = {
            'providers': providers,
            'total_providers': len(providers),
            'avg_rating': sum(p['details'].get('rating', 0) for p in providers) / len(providers) if providers else 0,
            'price_range': {
                'min': min(p['details'].get('avg_cost', 0) for p in providers) if providers else 0,
                'max': max(p['details'].get('avg_cost', 0) for p in providers) if providers else 0
            }
        }

        return comparison

    def get_popular_services(self) -> Dict[str, Any]:
        """Get popular services from both databases"""
        # This would typically query order history or service frequency
        # For now, return a curated list
        popular_services = [
            {'name': 'Emergency Plumbing', 'category': 'plumbing', 'demand': 'High'},
            {'name': 'Home Electrical Repair', 'category': 'electrical', 'demand': 'High'},
            {'name': 'Interior Painting', 'category': 'painting', 'demand': 'Medium'},
            {'name': 'Car Maintenance', 'category': 'automotive', 'demand': 'High'},
            {'name': 'AC Installation & Repair', 'category': 'hvac', 'demand': 'High'},
            {'name': 'Custom Furniture', 'category': 'carpentry', 'demand': 'Medium'},
            {'name': 'House Cleaning', 'category': 'cleaning', 'demand': 'Medium'},
            {'name': 'Garden Maintenance', 'category': 'landscaping', 'demand': 'Low'}
        ]

        return {
            'services': popular_services,
            'total_services': len(popular_services),
            'high_demand_count': len([s for s in popular_services if s['demand'] == 'High'])
        }

    def get_federated_search_results(self, user_query: str, limit: int = 15) -> Dict[str, Any]:
        """
        Advanced federated search with query federation, prompt rewriting, and results integration
        """
        try:
            # Run federated search with all advanced features
            federated_results = self.query_federation_engine.run_federated_search(user_query, limit)

            # Add additional analysis and metadata
            enhanced_results = {
                'federated_search': True,
                'query_analysis': federated_results['analysis'],
                'rewritten_prompt': federated_results['rewritten_prompt'],
                'search_plan': federated_results['plan'],
                'employees': federated_results['results'],
                'integration_summary': federated_results['integration_summary'],
                'research_highlights': federated_results['research_highlights'],

                # Enhanced metadata
                'query_complexity': self._analyze_query_complexity(user_query),
                'search_coverage': federated_results['integration_summary']['coverage'],
                'recommendation_confidence': self._calculate_recommendation_confidence(federated_results),
                'prompt_improvements': self._get_prompt_improvements(user_query, federated_results['rewritten_prompt'])
            }

            return enhanced_results

        except Exception as e:
            print(f"Error in federated search: {e}")
            # Fallback to basic search
            return self.get_intelligent_recommendations(user_query, 'both', limit)

    def get_prompt_rewrite_analysis(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze and show how the prompt rewriter improves user queries
        """
        try:
            # Get basic analysis
            analysis = self.llm_service.analyze_distributed_service_request(user_query, 'both')

            # Get rewritten prompt
            rewritten = self.prompt_rewriter.rewrite(user_query, analysis)

            return {
                'original_query': user_query,
                'rewritten_query': rewritten['canonical_query'],
                'extracted_keywords': rewritten['keywords'],
                'detected_region': rewritten['region'],
                'primary_intent': rewritten['primary_intent'],
                'provider_bias': rewritten['provider_bias'],
                'improvements': self._get_prompt_improvements(user_query, rewritten),
                'analysis_confidence': analysis.get('confidence_score', 0.0)
            }

        except Exception as e:
            print(f"Error in prompt rewrite analysis: {e}")
            return {
                'original_query': user_query,
                'error': str(e)
            }

    def get_results_integration_analysis(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze how results from different databases are integrated
        """
        try:
            # Get federated search results
            federated_results = self.query_federation_engine.run_federated_search(user_query, 20)
            integration_summary = federated_results['integration_summary']

            # Analyze integration quality
            analysis = {
                'query': user_query,
                'total_results': integration_summary['coverage']['combined'],
                'primary_database_results': integration_summary['coverage']['primary_matches'],
                'secondary_database_results': integration_summary['coverage']['secondary_matches'],
                'integration_quality': self._assess_integration_quality(integration_summary),
                'data_source_balance': self._calculate_source_balance(integration_summary),
                'top_providers': {
                    'primary': integration_summary['top_primary'],
                    'secondary': integration_summary['top_secondary']
                },
                'integration_notes': integration_summary['notes'],
                'recommendations': self._generate_integration_recommendations(integration_summary)
            }

            return analysis

        except Exception as e:
            print(f"Error in results integration analysis: {e}")
            return {
                'query': user_query,
                'error': str(e)
            }

    def _analyze_query_complexity(self, user_query: str) -> Dict[str, Any]:
        """Analyze the complexity of the user query"""
        words = len(user_query.split())
        has_location = any(word.lower() in ['downtown', 'uptown', 'north', 'south', 'east', 'west'] for word in user_query.split())
        has_urgency = any(word.lower() in ['emergency', 'urgent', 'asap', 'immediate'] for word in user_query.split())

        if words > 10 or has_urgency:
            complexity = "High"
        elif words > 5 or has_location:
            complexity = "Medium"
        else:
            complexity = "Low"

        return {
            'word_count': words,
            'has_location_hint': has_location,
            'has_urgency_hint': has_urgency,
            'complexity_level': complexity
        }

    def _calculate_recommendation_confidence(self, federated_results: Dict) -> float:
        """Calculate confidence in the recommendations"""
        try:
            analysis = federated_results.get('analysis', {})
            integration = federated_results.get('integration_summary', {})

            # Base confidence from LLM analysis
            llm_confidence = analysis.get('confidence_score', 0.5)

            # Boost confidence if we have good results
            total_results = integration.get('coverage', {}).get('combined', 0)
            if total_results > 10:
                result_boost = 0.2
            elif total_results > 5:
                result_boost = 0.1
            else:
                result_boost = 0.0

            # Boost if we have both data sources
            primary = integration.get('coverage', {}).get('primary_matches', 0)
            secondary = integration.get('coverage', {}).get('secondary_matches', 0)
            if primary > 0 and secondary > 0:
                source_boost = 0.1
            else:
                source_boost = 0.0

            confidence = min(0.95, llm_confidence + result_boost + source_boost)
            return round(confidence, 2)

        except:
            return 0.5

    def _get_prompt_improvements(self, original: str, rewritten: Dict) -> List[str]:
        """Get list of prompt improvements made"""
        improvements = []

        if rewritten.get('keywords') and len(rewritten['keywords']) > 0:
            improvements.append(f"Added {len(rewritten['keywords'])} relevant keywords")

        if rewritten.get('region'):
            improvements.append(f"Detected location: {rewritten['region']}")

        if rewritten.get('primary_intent') and rewritten['primary_intent'] != 'general':
            improvements.append(f"Identified service type: {rewritten['primary_intent']}")

        if rewritten.get('provider_bias') and rewritten['provider_bias'] != 'both':
            improvements.append(f"Determined provider preference: {rewritten['provider_bias']}")

        return improvements if improvements else ["Query optimized for search"]

    def _assess_integration_quality(self, integration_summary: Dict) -> str:
        """Assess the quality of result integration"""
        coverage = integration_summary.get('coverage', {})
        total = coverage.get('combined', 0)
        primary = coverage.get('primary_matches', 0)
        secondary = coverage.get('secondary_matches', 0)

        if total == 0:
            return "Poor - No results found"
        elif total < 5:
            return "Fair - Limited results"
        elif primary > 0 and secondary > 0:
            return "Excellent - Balanced results from both databases"
        elif primary > 10 or secondary > 10:
            return "Good - Strong results from one database"
        else:
            return "Good - Decent results available"

    def _calculate_source_balance(self, integration_summary: Dict) -> str:
        """Calculate the balance between data sources"""
        coverage = integration_summary.get('coverage', {})
        primary = coverage.get('primary_matches', 0)
        secondary = coverage.get('secondary_matches', 0)

        if primary == 0 and secondary == 0:
            return "No results"
        elif primary == 0:
            return "Secondary only"
        elif secondary == 0:
            return "Primary only"
        elif abs(primary - secondary) <= 2:
            return "Balanced"
        elif primary > secondary:
            return "Primary dominant"
        else:
            return "Secondary dominant"

    def _generate_integration_recommendations(self, integration_summary: Dict) -> List[str]:
        """Generate recommendations based on integration analysis"""
        recommendations = []
        coverage = integration_summary.get('coverage', {})
        primary = coverage.get('primary_matches', 0)
        secondary = coverage.get('secondary_matches', 0)

        if primary == 0 and secondary == 0:
            recommendations.append("Try using different keywords or broader search terms")
            recommendations.append("Consider checking spelling or service category")
        elif primary > 0 and secondary == 0:
            recommendations.append("Results from companies only - consider individual workers for potentially better rates")
        elif primary == 0 and secondary > 0:
            recommendations.append("Results from individual workers only - companies may offer better warranty coverage")
        else:
            recommendations.append("Good balance of companies and individual workers available")

        return recommendations