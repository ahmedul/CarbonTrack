"""
Carbon Reduction Recommendation Engine

Analyzes user emission patterns and provides intelligent, personalized recommendations
based on scientific data and best practices for carbon footprint reduction.
"""

from typing import Dict, List, Any
from datetime import datetime
import logging

from app.services.carbon_calculator import calculator

logger = logging.getLogger(__name__)


class RecommendationCategory:
    """Categories for recommendations"""
    TRANSPORTATION = "transportation"
    ENERGY = "energy"
    FOOD = "food"
    WASTE = "waste"
    LIFESTYLE = "lifestyle"


class RecommendationEngine:
    """
    Intelligent carbon reduction recommendation system
    
    Analyzes user's emission patterns and provides personalized,
    actionable recommendations based on scientific emission factors.
    """
    
    def __init__(self):
        self.calculator = calculator
        
        # Recommendation templates with impact calculations
        self.recommendations = {
            RecommendationCategory.TRANSPORTATION: [
                {
                    "id": "switch_to_electric",
                    "title": "Switch to Electric Vehicle",
                    "description": "Electric vehicles produce 60-70% fewer emissions than gasoline cars",
                    "action": "Consider an electric or hybrid vehicle for your next purchase",
                    "potential_savings_factor": 0.65,  # 65% reduction
                    "difficulty": "medium",
                    "cost": "high",
                    "timeframe": "long-term",
                    "category": "vehicle",
                    "triggers": ["car_gasoline_medium", "car_gasoline_large", "car_gasoline_small"]
                },
                {
                    "id": "use_public_transport",
                    "title": "Use Public Transportation",
                    "description": "Buses and trains produce 45-80% fewer emissions per passenger than cars",
                    "action": "Use public transport, carpool, or bike for short trips",
                    "potential_savings_factor": 0.75,
                    "difficulty": "easy",
                    "cost": "low",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["car_gasoline_medium", "car_gasoline_large", "car_gasoline_small"]
                },
                {
                    "id": "reduce_flights",
                    "title": "Minimize Air Travel",
                    "description": "Aviation is one of the most carbon-intensive activities",
                    "action": "Consider virtual meetings or train travel for shorter distances",
                    "potential_savings_factor": 0.80,
                    "difficulty": "medium",
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["flight_domestic_short", "flight_domestic_medium", "flight_international"]
                },
                {
                    "id": "optimize_driving",
                    "title": "Optimize Driving Habits",
                    "description": "Eco-friendly driving can reduce fuel consumption by 15-20%",
                    "action": "Drive smoothly, maintain proper tire pressure, and combine trips",
                    "potential_savings_factor": 0.18,
                    "difficulty": "easy",
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["car_gasoline_medium", "car_gasoline_large", "car_gasoline_small"]
                }
            ],
            
            RecommendationCategory.ENERGY: [
                {
                    "id": "switch_to_renewables",
                    "title": "Switch to Renewable Energy",
                    "description": "Renewable energy can reduce your home's carbon footprint by 80-100%",
                    "action": "Contact your utility about renewable energy programs or install solar panels",
                    "potential_savings_factor": 0.85,
                    "difficulty": "medium",
                    "cost": "medium",
                    "timeframe": "medium-term",
                    "category": "infrastructure",
                    "triggers": ["electricity"]
                },
                {
                    "id": "improve_insulation",
                    "title": "Improve Home Insulation",
                    "description": "Better insulation can reduce heating/cooling energy use by 30-50%",
                    "action": "Add insulation, seal air leaks, upgrade windows",
                    "potential_savings_factor": 0.40,
                    "difficulty": "medium",
                    "cost": "medium",
                    "timeframe": "medium-term",
                    "category": "infrastructure", 
                    "triggers": ["natural_gas_therms", "heating_oil_gallons", "electricity"]
                },
                {
                    "id": "efficient_appliances",
                    "title": "Use Energy-Efficient Appliances",
                    "description": "ENERGY STAR appliances use 10-25% less energy",
                    "action": "Replace old appliances with ENERGY STAR certified models",
                    "potential_savings_factor": 0.20,
                    "difficulty": "easy",
                    "cost": "medium",
                    "timeframe": "medium-term",
                    "category": "appliances",
                    "triggers": ["electricity"]
                },
                {
                    "id": "smart_thermostat",
                    "title": "Install Smart Thermostat",
                    "description": "Smart thermostats can reduce heating/cooling costs by 10-15%",
                    "action": "Install a programmable or smart thermostat",
                    "potential_savings_factor": 0.12,
                    "difficulty": "easy",
                    "cost": "low",
                    "timeframe": "immediate",
                    "category": "technology",
                    "triggers": ["natural_gas_therms", "electricity"]
                }
            ],
            
            RecommendationCategory.FOOD: [
                {
                    "id": "reduce_beef_consumption",
                    "title": "Reduce Beef Consumption",
                    "description": "Beef has the highest carbon footprint of common foods (60kg CO₂/kg)",
                    "action": "Replace beef meals with chicken, fish, or plant-based alternatives",
                    "potential_savings_factor": 0.85,  # Switching beef to chicken
                    "difficulty": "easy",
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "diet",
                    "triggers": ["beef"]
                },
                {
                    "id": "eat_more_plants",
                    "title": "Adopt Plant-Rich Diet",
                    "description": "Plant-based meals typically have 75% lower emissions than meat-based meals",
                    "action": "Try \"Meatless Monday\" or plant-based meals 2-3 times per week",
                    "potential_savings_factor": 0.75,
                    "difficulty": "easy",
                    "cost": "low",
                    "timeframe": "immediate",
                    "category": "diet",
                    "triggers": ["beef", "lamb", "pork"]
                },
                {
                    "id": "choose_local_seasonal",
                    "title": "Choose Local & Seasonal Foods",
                    "description": "Local, seasonal produce reduces transportation emissions by up to 50%",
                    "action": "Shop at farmers markets and choose seasonal produce",
                    "potential_savings_factor": 0.30,
                    "difficulty": "easy",
                    "cost": "low",
                    "timeframe": "immediate",
                    "category": "sourcing",
                    "triggers": ["fruits_tropical", "vegetables_leafy"]
                },
                {
                    "id": "reduce_food_waste",
                    "title": "Minimize Food Waste",
                    "description": "Food waste in landfills produces methane, a potent greenhouse gas",
                    "action": "Plan meals, store food properly, and compost scraps",
                    "potential_savings_factor": 0.40,
                    "difficulty": "easy",
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["landfill_food"]
                }
            ],
            
            RecommendationCategory.WASTE: [
                {
                    "id": "increase_recycling",
                    "title": "Maximize Recycling",
                    "description": "Recycling saves significant emissions compared to landfill disposal",
                    "action": "Separate recyclables properly and learn your local recycling guidelines",
                    "potential_savings_factor": 0.60,
                    "difficulty": "easy",
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["landfill_mixed"]
                },
                {
                    "id": "start_composting",
                    "title": "Start Home Composting",
                    "description": "Composting eliminates methane emissions from organic waste in landfills",
                    "action": "Set up a compost bin or use municipal composting services",
                    "potential_savings_factor": 0.80,
                    "difficulty": "easy",
                    "cost": "low",
                    "timeframe": "immediate",
                    "category": "infrastructure",
                    "triggers": ["landfill_food"]
                },
                {
                    "id": "reduce_packaging",
                    "title": "Choose Less Packaging",
                    "description": "Packaging creates emissions during production and disposal",
                    "action": "Buy in bulk, choose products with minimal packaging, bring reusable bags",
                    "potential_savings_factor": 0.25,
                    "difficulty": "easy", 
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["landfill_mixed", "recycling_plastic"]
                }
            ],
            
            RecommendationCategory.LIFESTYLE: [
                {
                    "id": "remote_work",
                    "title": "Work from Home More Often",
                    "description": "Remote work can eliminate commuting emissions entirely",
                    "action": "Negotiate flexible work arrangements or remote work days",
                    "potential_savings_factor": 1.0,  # Eliminates commute
                    "difficulty": "medium",
                    "cost": "none",
                    "timeframe": "immediate",
                    "category": "behavior",
                    "triggers": ["car_gasoline_medium", "car_gasoline_large"]
                },
                {
                    "id": "carbon_offset",
                    "title": "Purchase Carbon Offsets",
                    "description": "High-quality offsets can neutralize remaining emissions",
                    "action": "Research certified carbon offset programs for unavoidable emissions",
                    "potential_savings_factor": 1.0,
                    "difficulty": "easy",
                    "cost": "low",
                    "timeframe": "immediate",
                    "category": "offset",
                    "triggers": []  # Always applicable
                }
            ]
        }
    
    def analyze_user_patterns(self, emissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user's emission patterns to understand their carbon footprint profile
        
        Args:
            emissions: List of user's emission entries
            
        Returns:
            Analysis results with patterns, top categories, and key insights
        """
        if not emissions:
            return {
                "total_emissions": 0,
                "category_breakdown": {},
                "top_activities": [],
                "patterns": {},
                "insights": []
            }
        
        # Calculate totals by category and activity
        category_totals = {}
        activity_totals = {}
        monthly_trends = {}
        
        for emission in emissions:
            category = emission.get("category", "unknown")
            activity = emission.get("activity", "unknown") 
            co2 = float(emission.get("co2_equivalent", 0))
            date_str = emission.get("date", "")
            
            # Category totals
            category_totals[category] = category_totals.get(category, 0) + co2
            
            # Activity totals
            activity_key = f"{category}:{activity}"
            activity_totals[activity_key] = activity_totals.get(activity_key, 0) + co2
            
            # Monthly trends
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                monthly_trends[month_key] = monthly_trends.get(month_key, 0) + co2
            except Exception:
                pass
        
        # Sort activities by impact
        top_activities = sorted(activity_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate insights
        total_emissions = sum(category_totals.values())
        insights = self._generate_insights(category_totals, activity_totals, total_emissions)
        
        return {
            "total_emissions": round(total_emissions, 2),
            "category_breakdown": {k: round(v, 2) for k, v in category_totals.items()},
            "top_activities": [(activity.split(':')[1], round(co2, 2)) for activity, co2 in top_activities],
            "monthly_trends": {k: round(v, 2) for k, v in monthly_trends.items()},
            "patterns": self._identify_patterns(category_totals, total_emissions),
            "insights": insights
        }
    
    def generate_recommendations(self, emissions: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
        """
        Generate personalized carbon reduction recommendations
        
        Args:
            emissions: User's emission entries
            limit: Maximum number of recommendations to return
            
        Returns:
            List of personalized recommendations with impact estimates
        """
        if not emissions:
            # Return general recommendations for new users
            return self._get_general_recommendations(limit)
        
        # Analyze user patterns
        analysis = self.analyze_user_patterns(emissions)
        
        # Get user activities
        user_activities = set()
        for emission in emissions:
            user_activities.add(emission.get("activity", ""))
        
        # Score and rank recommendations
        scored_recommendations = []
        
        for category, recs in self.recommendations.items():
            for rec in recs:
                score = self._score_recommendation(rec, analysis, user_activities, emissions)
                if score > 0:
                    rec_with_score = rec.copy()
                    rec_with_score["score"] = score
                    rec_with_score["estimated_annual_savings"] = self._calculate_potential_savings(
                        rec, analysis, emissions
                    )
                    scored_recommendations.append(rec_with_score)
        
        # Sort by score and return top recommendations
        scored_recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_recommendations[:limit]
    
    def _generate_insights(self, category_totals: Dict, activity_totals: Dict, total_emissions: float) -> List[str]:
        """Generate insights about user's carbon footprint"""
        insights = []
        
        if total_emissions == 0:
            return ["Start tracking your activities to get personalized insights!"]
        
        # Category insights
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            top_percentage = (category_totals[top_category] / total_emissions) * 100
            insights.append(f"{top_category.title()} makes up {top_percentage:.0f}% of your carbon footprint")
        
        # Comparison to average
        # Average American: ~16 tons CO2/year = ~1.33 tons/month
        monthly_avg = total_emissions  # Assuming monthly data for demo
        if monthly_avg > 1.5:
            insights.append("Your emissions are above average - great opportunity for reduction!")
        elif monthly_avg < 0.8:
            insights.append("You're doing great! Your emissions are below average.")
        else:
            insights.append("Your emissions are close to average - small changes can make a big impact.")
        
        # Activity-specific insights
        beef_emissions = sum(co2 for (activity, co2) in activity_totals.items() if "beef" in activity.lower())
        if beef_emissions > 10:  # >10kg CO2 from beef
            insights.append("Reducing beef consumption could significantly lower your food footprint")
        
        car_emissions = sum(co2 for (activity, co2) in activity_totals.items() if "car_gasoline" in activity.lower())
        if car_emissions > 20:  # >20kg CO2 from cars
            insights.append("Transportation is a major contributor - consider alternatives for some trips")
        
        return insights
    
    def _identify_patterns(self, category_totals: Dict, total_emissions: float) -> Dict[str, Any]:
        """Identify patterns in user's emissions"""
        if total_emissions == 0:
            return {}
        
        patterns = {}
        
        # Dominant category
        if category_totals:
            dominant_category = max(category_totals, key=category_totals.get)
            dominant_percentage = (category_totals[dominant_category] / total_emissions) * 100
            patterns["dominant_category"] = {
                "category": dominant_category,
                "percentage": round(dominant_percentage, 1)
            }
        
        # Emission distribution
        if len(category_totals) > 1:
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            if sorted_categories[0][1] > sorted_categories[1][1] * 3:
                patterns["distribution"] = "concentrated"  # One category dominates
            else:
                patterns["distribution"] = "balanced"  # More evenly distributed
        
        return patterns
    
    def _score_recommendation(self, rec: Dict, analysis: Dict, user_activities: set, emissions: List) -> float:
        """Score a recommendation based on relevance to user"""
        score = 0
        
        # Check if user has relevant activities
        triggers = rec.get("triggers", [])
        if triggers:
            has_trigger_activity = any(activity in user_activities for activity in triggers)
            if not has_trigger_activity:
                return 0  # Not relevant
        
        # Base score from potential impact
        score += rec.get("potential_savings_factor", 0) * 50  # 0-50 points
        
        # Bonus for easy/immediate actions
        if rec.get("difficulty") == "easy":
            score += 10
        if rec.get("timeframe") == "immediate":
            score += 10
        if rec.get("cost") in ["none", "low"]:
            score += 5
        
        # Category relevance bonus
        category_breakdown = analysis.get("category_breakdown", {})
        rec_category = None
        for cat in category_breakdown:
            if cat in rec.get("triggers", []):
                rec_category = cat
                break
        
        if rec_category and category_breakdown.get(rec_category, 0) > 0:
            # Higher score for categories with more emissions
            category_percentage = category_breakdown[rec_category] / analysis.get("total_emissions", 1)
            score += category_percentage * 20  # Up to 20 bonus points
        
        return score
    
    def _calculate_potential_savings(self, rec: Dict, analysis: Dict, emissions: List) -> float:
        """Calculate potential annual CO2 savings from recommendation"""
        if not emissions or analysis.get("total_emissions", 0) == 0:
            return 0
        
        triggers = rec.get("triggers", [])
        if not triggers:
            # General recommendation - estimate based on total emissions
            return analysis["total_emissions"] * rec.get("potential_savings_factor", 0) * 12  # Annualize
        
        # Calculate savings for specific activities
        relevant_emissions = 0
        for emission in emissions:
            if emission.get("activity") in triggers:
                relevant_emissions += float(emission.get("co2_equivalent", 0))
        
        # Annual estimate (assuming monthly data)
        annual_relevant = relevant_emissions * 12
        potential_savings = annual_relevant * rec.get("potential_savings_factor", 0)
        
        return round(potential_savings, 1)
    
    def _get_general_recommendations(self, limit: int) -> List[Dict[str, Any]]:
        """Get general recommendations for new users"""
        general_recs = []
        
        # Pick top recommendations from each category
        for category, recs in self.recommendations.items():
            if general_recs and len(general_recs) >= limit:
                break
            
            # Get the easiest/most impactful recommendation from this category
            category_best = max(
                recs, 
                key=lambda r: (
                    r.get("potential_savings_factor", 0) * 0.7 +
                    (0.3 if r.get("difficulty") == "easy" else 0) +
                    (0.2 if r.get("cost") in ["none", "low"] else 0)
                )
            )
            
            rec_copy = category_best.copy()
            rec_copy["estimated_annual_savings"] = 0  # Can't calculate without data
            general_recs.append(rec_copy)
        
        return general_recs[:limit]


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()