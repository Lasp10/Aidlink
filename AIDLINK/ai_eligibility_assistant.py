#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_FILE = os.getenv('AIDLINK_ENV_FILE', 'aidlink.env')
env_path = Path(ENV_FILE)
if env_path.exists():
    load_dotenv(env_path)

class AIEligibilityAssistant:
    """
    AI-Powered Eligibility Navigator
    Uses Gemini to understand complex situations and determine program eligibility
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        # Check if API key is set and not a placeholder
        if self.api_key and self.api_key != 'replace_with_gemini_key' and not self.api_key.startswith('replace_with'):
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.available = True
                print("✅ Gemini API configured")
            except Exception as e:
                self.available = False
                print(f"⚠️ Gemini API configuration error: {e}")
        else:
            self.available = False
            print("⚠️ Gemini API key not configured - using fallback mode")
            print("   Get a free API key at: https://aistudio.google.com/app/apikey")
    
    def analyze_user_situation(self, user_input: str, context: Dict = None, location: str = None) -> Dict[str, Any]:
        """
        Analyze user's situation and determine what programs they likely qualify for
        
        Args:
            user_input: Natural language description of user's situation
            context: Optional context (previous responses, location, etc.)
            location: User's location for location-specific recommendations
        
        Returns:
            Comprehensive analysis with eligibility assessment
        """
        if not self.available:
            return self._fallback_analysis(user_input)
        
        try:
            # Build comprehensive prompt
            location_context = f"\n\nUser Location: {location}" if location else ""
            prompt = f"""
You are an expert social services eligibility navigator. Your job is to analyze a person's situation and determine what government and community assistance programs they might qualify for.

User Situation: "{user_input}"{location_context}

IMPORTANT: Focus on programs and resources available in the user's specific location. If a location is provided, prioritize local programs, services, and organizations in that area.

Please provide a comprehensive analysis in JSON format with:
1. situation_summary: Brief summary of their situation
2. key_factors: List of important factors (homeless, unemployed, has_children, etc.)
3. likely_eligible_programs: Array of programs they likely qualify for
4. program_details: For each program, provide:
   - name: Program name
   - category: food, housing, employment, etc.
   - confidence: How likely they qualify (0-1)
   - why_they_qualify: Specific reasons
   - what_they_need: Required documents/requirements
   - how_to_apply: Next steps (include location-specific contact info if location provided)
5. urgency_score: How urgent their needs are (1-10)
6. priority_order: Recommended order to address needs
7. barriers_identified: List of potential obstacles
8. barrier_solutions: Solutions for each barrier

IMPORTANT: Respond with ONLY valid JSON. Start with {{ and end with }}.
"""
            
            if context:
                prompt += f"\n\nAdditional Context: {json.dumps(context)}"
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
            
            result = json.loads(response_text)
            
            return {
                'success': True,
                'analysis': result,
                'ai_model': 'gemini-pro',
                'confidence': result.get('confidence', 0.85)
            }
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_analysis(user_input)
    
    def create_action_plan_from_resources(self, analysis: Dict[str, Any], resources: List[Dict], location: str = None) -> Dict[str, Any]:

        if not self.available or not resources:
            return self._get_immediate_action_plan(analysis, location)
        
        # Take only the BEST 2-3 resources
        best_resources = resources[:3]
        
        try:
            location_context = f"\n\nUser Location: {location}" if location else ""
            prompt = f"""
User needs help, you found these resources. Create a DETAILED action plan.

User situation: {analysis.get('analysis', {}).get('situation_summary', 'Need assistance')}{location_context}

Actual Resources Found (these are REAL resources in the user's area):
{json.dumps(best_resources, indent=2)}

IMPORTANT: These resources are location-specific. Use the EXACT names, addresses, and phone numbers from the resources above. The user is in {location or 'their local area'}.

Create action plan with 2-3 detailed steps using THESE EXACT resources.

Return this JSON format:
{{
  "urgent_actions": [
    {{
      "action": "What to do with this specific resource (use exact resource name)",
      "why": "Why this resource helps their situation",
      "phone_number": "exact phone from resource above",
      "address": "exact address from resource above",
      "timeframe": "When to do this (today/this week)"
    }}
  ]
}}

RULES:
- Use ACTUAL resource names, phones, addresses from the resources list above
- Include context (why it helps)
- Add timeframe for each action
- Be specific to their situation
- 2-3 steps max
- Prioritize resources with transportation assistance or shorter distances
- All resources must be from the list above - do not make up resources

Return JSON only.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
            
            action_plan = json.loads(response_text)
            
            # Ensure we only have 2-3 actions max
            if 'urgent_actions' in action_plan:
                action_plan['urgent_actions'] = action_plan['urgent_actions'][:3]
            
            return {
                'success': True,
                'action_plan': action_plan,
                'ai_model': 'gemini-pro'
            }
            
        except Exception as e:
            print(f"Action plan from resources error: {e}")
            return self._get_immediate_action_plan(analysis, location)
    
    def create_action_plan(self, analysis: Dict[str, Any], location: str = None) -> Dict[str, Any]:
        """
        Generate intelligent action plan based on eligibility analysis
        
        Args:
            analysis: Output from analyze_user_situation
            location: User's location for local recommendations
        
        Returns:
            Step-by-step action plan prioritized by urgency with SPECIFIC actionable items
        """
        if not self.available:
            return self._get_immediate_action_plan(analysis, location)
        
        try:
            # Create comprehensive action plan
            user_location = location or 'Sacramento, CA'
            prompt = f"""
Based on this eligibility analysis, create a COMPREHENSIVE action plan that helps someone take real steps.

Analysis:
{json.dumps(analysis.get('analysis', {}), indent=2)}

User Location: {user_location}

CRITICAL: The user is located in {user_location}. You MUST provide location-specific resources, addresses, phone numbers, and organizations that are actually in or near {user_location}. Do NOT use generic examples - use real, specific resources for {user_location}.

Generate a detailed action plan with:
1. Immediate actions (today)
2. This week actions
3. This month actions

Return JSON with:
{{
  "urgent_actions": [
    {{
      "action": "Specific, actionable step with location-specific details (what to do)",
      "why": "Why this matters for them",
      "phone_number": "actual phone number for {user_location} area",
      "address": "specific address in {user_location}",
      "timeframe": "When to do this (today, this week, this month)",
      "documents_needed": "What they need to bring/prepare"
    }}
  ],
  "timeline": "Overall expected timeline",
  "priority_order": "What to do first, second, third",
  "encouragement": "A supportive message to motivate them"
}}

RULES:
- Be specific and actionable
- Include real phone numbers for {user_location} area when possible
- Provide specific addresses in {user_location}
- Focus on resources actually available in {user_location}
- Provide context (why each step matters)
- Make it encouraging, not overwhelming
- Max 5 actions total
- IMPORTANT: All resources must be location-specific to {user_location}

Example structure for {user_location}:
{{
  "urgent_actions": [
    {{"action": "Call 211 today to speak with a resource specialist in {user_location}", "why": "211 connects you to local assistance programs in your area", "phone_number": "211", "address": "Dial 2-1-1 from any phone - available in {user_location}", "timeframe": "today", "documents_needed": "None - just your situation"}},
    {{"action": "Contact local food assistance programs in {user_location}", "why": "You mentioned food insecurity - local programs provide immediate help", "phone_number": "Check 211 or local food bank", "address": "Search for food banks in {user_location}", "timeframe": "today", "documents_needed": "None required"}}
  ],
  "timeline": "You should see progress within 24-48 hours",
  "priority_order": "1. Call 211 first (they connect you to everything in {user_location}), 2. Contact local food assistance if hungry today, 3. Apply for benefits this week",
  "encouragement": "You're taking the right steps! Help is available in {user_location} and you're not alone."
}}

Respond with ONLY valid JSON.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
            
            action_plan = json.loads(response_text)
            
            # Enhance with real Sacramento resources if available
            try:
                from demo_211_data import get_demo_211_data
                demo_data_available = True
            except ImportError:
                demo_data_available = False
            
            if demo_data_available and location:
                action_plan = self._enhance_with_real_resources(action_plan, location)
            
            return {
                'success': True,
                'action_plan': action_plan,
                'ai_model': 'gemini-pro'
            }
            
        except Exception as e:
            print(f"Action plan generation error: {e}")
            return self._get_immediate_action_plan(analysis, location)
    
    def _enhance_with_real_resources(self, action_plan: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Enhance action plan - no demo data, just return as-is"""
        # No longer using demo data, just return the action plan as provided by AI
        return action_plan
    
    def _get_immediate_action_plan(self, analysis: Dict[str, Any], location: str = None) -> Dict[str, Any]:
        """Generate action plan without demo data - simple fallback"""
        # Simple fallback: just use the analysis to create basic actions
        key_factors = analysis.get('analysis', {}).get('key_factors', [])
        situation_summary = analysis.get('analysis', {}).get('situation_summary', '')
        
        urgent_actions = []
        
        # Food emergency
        if any('food' in str(f).lower() or 'hungry' in str(f).lower() or 'hunger' in str(f).lower() for f in key_factors):
            urgent_actions.append({
                'action': 'Call 211 for immediate food assistance',
                'phone_number': '211',
                'address': 'Call 211 or visit 211.org',
            })
        
        # Housing emergency
        if any('home' in str(f).lower() or 'shelter' in str(f).lower() or 'housing' in str(f).lower() or 'homeless' in str(f).lower() for f in key_factors):
            urgent_actions.append({
                'action': 'Call 211 for emergency housing assistance',
                'phone_number': '211',
                'address': 'Call 211 or visit 211.org',
            })
        
        # Always add 211
        if not urgent_actions or len(urgent_actions) < 3:
            urgent_actions.append({
                'action': 'Call 211 for all resources',
                'phone_number': '211',
                'address': 'Available 24/7 - dial 2-1-1',
            })
        
        return {
            'success': True,
            'action_plan': {
                'prioritized_action_plan': {
                    'urgent_actions': urgent_actions[:3],  # Limit to 3
                    'estimated_timeline': 'Contact 211 today for immediate assistance'
                }
            },
            'ai_model': 'simple_fallback'
        }
    
    def suggest_followup_questions(self, current_situation: str) -> List[str]:
        """
        Generate intelligent follow-up questions to better understand user's situation
        
        Args:
            current_situation: What we know so far
        
        Returns:
            List of questions to ask
        """
        if not self.available:
            return [
                "Are you currently working?",
                "Do you have housing right now?",
                "Are there children in your household?"
            ]
        
        try:
            prompt = f"""
User's current situation: "{current_situation}"

Generate 3-5 follow-up questions that would help you better understand their situation and find appropriate resources.

Focus on questions about:
- Housing stability
- Employment status
- Family situation
- Income
- Specific urgent needs

Return as JSON array of questions: ["question 1", "question 2", etc.]

Respond with ONLY valid JSON array.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
            
            questions = json.loads(response_text)
            
            return questions if isinstance(questions, list) else []
            
        except Exception as e:
            print(f"Question generation error: {e}")
            return ["Tell me more about your situation"]
    
    def translate_government_jargon(self, text: str) -> str:
        """
        Translate complex government eligibility requirements into plain English
        """
        if not self.available:
            return text
        
        try:
            prompt = f"""
Translate this government eligibility requirement into simple, clear language that anyone can understand:

Original: "{text}"

Provide a translation that:
1. Explains what it actually means
2. Gives examples
3. Tells them if they likely qualify

Respond with ONLY the translated text, no explanations.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return text
    
    def identify_barriers(self, situation: str, resources: List[Dict]) -> Dict[str, Any]:
        """
        Identify potential barriers to accessing resources and suggest solutions
        """
        if not self.available or not resources:
            return {'barriers': [], 'solutions': []}
        
        try:
            # Summarize resources
            resource_summary = "\n".join([
                f"- {r.get('name', 'Unknown')}: {r.get('eligibility', 'No requirements')}"
                for r in resources[:5]
            ])
            
            prompt = f"""
User Situation: "{situation}"

Available Resources:
{resource_summary}

Identify potential barriers to accessing these resources (transportation, documentation, language, time, etc.) and suggest solutions.

Return JSON with:
{{
  "barriers": [
    {{"issue": "problem", "impact": "how it affects them", "solutions": ["solution 1", "solution 2"]}}
  ]
}}

Respond with ONLY valid JSON.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            print(f"Barrier identification error: {e}")
            return {'barriers': [], 'solutions': []}
    
    def generate_document_checklist(self, analysis: Dict[str, Any], action_plan: Dict[str, Any] = None) -> List[str]:
        """
        Generate personalized document checklist based on user's situation and planned actions
        
        Args:
            analysis: Output from analyze_user_situation
            action_plan: Optional action plan to tailor documents needed
        
        Returns:
            List of documents the user will likely need
        """
        if not self.available:
            return self._basic_document_checklist(analysis)
        
        try:
            situation = analysis.get('analysis', {}).get('situation_summary', '')
            key_factors = analysis.get('analysis', {}).get('key_factors', [])
            eligible_programs = analysis.get('analysis', {}).get('likely_eligible_programs', [])
            
            prompt = f"""
Based on this person's situation, create a personalized checklist of documents they will need to apply for assistance programs.

Situation: {situation}
Key factors: {', '.join(str(f) for f in key_factors[:5])}
Eligible programs: {', '.join(str(p) for p in eligible_programs[:5]) if eligible_programs else 'General assistance'}

Generate a SPECIFIC, ACTIONABLE document checklist. Only include documents that are actually needed for their situation.

Common documents include (but only list relevant ones):
- Government-issued ID (driver's license, state ID, passport)
- Social Security card or proof of SSN
- Proof of income (pay stubs, tax returns, letter from employer)
- Proof of expenses (rent receipts, utility bills, medical bills)
- Proof of residence (lease, utility bill, mail with address)
- Birth certificates (for children in household)
- Proof of citizenship/immigration status
- Medical records (if applying for health-related assistance)
- Bank statements
- Proof of unemployment (if applicable)

Return as JSON array of document names:
["Document 1", "Document 2", "Document 3"]

Be specific and personalized to their situation. Return ONLY the JSON array.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
                documents = json.loads(response_text)
                # Ensure basic documents are always included
                basic_docs = ['Government-issued ID (driver\'s license or state ID)']
                for doc in basic_docs:
                    if doc not in documents:
                        documents.insert(0, doc)
                return documents[:10]  # Limit to 10 documents
            
            return self._basic_document_checklist(analysis)
            
        except Exception as e:
            print(f"Document checklist generation error: {e}")
            return self._basic_document_checklist(analysis)
    
    def _basic_document_checklist(self, analysis: Dict[str, Any]) -> List[str]:
        """Basic fallback document checklist"""
        docs = ['Government-issued ID (driver\'s license or state ID)']
        
        situation_lower = str(analysis.get('analysis', {}).get('situation_summary', '')).lower()
        
        if 'income' in situation_lower or 'job' in situation_lower or 'unemployed' in situation_lower:
            docs.append('Proof of income (pay stubs, tax returns, or unemployment letter)')
        
        if 'housing' in situation_lower or 'rent' in situation_lower or 'homeless' in situation_lower:
            docs.append('Proof of residence (lease or utility bill) or statement of homelessness')
        
        if 'child' in situation_lower or 'kid' in situation_lower or 'family' in situation_lower:
            docs.append('Birth certificates for children in household')
            docs.append('Social Security cards for all household members')
        
        docs.append('Bank statements (last 2-3 months)')
        docs.append('Social Security card or proof of SSN')
        
        return docs[:8]
    
    def _fallback_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback when Gemini is not available"""
        return {
            'success': True,
            'analysis': {
                'situation_summary': user_input,
                'key_factors': self._extract_key_factors(user_input),
                'likely_eligible_programs': self._basic_program_match(user_input),
                'urgency_score': 5
            },
            'ai_model': 'basic_analysis',
            'confidence': 0.6
        }
    
    def _fallback_action_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback action plan"""
        return {
            'success': True,
            'action_plan': {
                'urgent_actions': [],
                'important_actions': [],
                'estimated_timeline': '2-4 weeks'
            },
            'ai_model': 'basic_planner'
        }
    
    def _extract_key_factors(self, text: str) -> List[str]:
        """Basic extraction of key factors"""
        factors = []
        text_lower = text.lower()
        
        if 'home' in text_lower or 'shelter' in text_lower:
            factors.append('housing_crisis')
        if 'job' in text_lower or 'unemployed' in text_lower or 'laid off' in text_lower:
            factors.append('unemployed')
        if 'child' in text_lower or 'kid' in text_lower:
            factors.append('has_children')
        if 'food' in text_lower or 'hungry' in text_lower:
            factors.append('food_insecure')
        if 'urgent' in text_lower or 'emergency' in text_lower:
            factors.append('urgent_need')
        
        return factors if factors else ['general_assistance_needed']
    
    def _basic_program_match(self, text: str) -> List[Dict[str, Any]]:
        """Basic program matching"""
        programs = []
        text_lower = text.lower()
        
        if 'food' in text_lower or 'hungry' in text_lower:
            programs.append({
                'name': 'SNAP Benefits',
                'category': 'food',
                'confidence': 0.7,
                'why_they_qualify': 'Food assistance available',
                'how_to_apply': 'Contact local social services office'
            })
        
        if 'home' in text_lower or 'shelter' in text_lower:
            programs.append({
                'name': 'Emergency Shelter Services',
                'category': 'housing',
                'confidence': 0.8,
                'why_they_qualify': 'Housing insecurity',
                'how_to_apply': 'Call 211 or local shelter'
            })
        
        return programs


def demo():
    """Demo the AI Eligibility Assistant"""
    print("=" * 70)
    print("AI ELIGIBILITY ASSISTANT - DEMO")
    print("=" * 70)
    
    assistant = AIEligibilityAssistant()
    
    test_cases = [
        "I'm homeless with 2 kids. Lost my job last month. Staying with a friend but only for 2 more weeks.",
        "I need food assistance. I'm unemployed and have no income.",
        "I'm a single mom with a 5-year-old. I'm behind on rent and need help."
    ]
    
    for i, situation in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST CASE {i}")
        print(f"{'='*70}")
        print(f"\nUser Situation:\n{situation}\n")
        
        # Analyze situation
        analysis = assistant.analyze_user_situation(situation)
        
        if analysis['success']:
            an_data = analysis['analysis']
            
            print("AI Analysis:")
            print(f"  Summary: {an_data.get('situation_summary', 'N/A')}")
            print(f"  Key Factors: {', '.join(an_data.get('key_factors', []))}")
            print(f"  Urgency: {an_data.get('urgency_score', 0)}/10")
            
            programs = an_data.get('likely_eligible_programs', [])
            print(f"\nLikely Eligible Programs ({len(programs)}):")
            for program in programs:
                print(f"  - {program.get('name', 'Unknown')} ({program.get('category', 'N/A')})")
                print(f"    Confidence: {program.get('confidence', 0)}")
                print(f"    Why: {program.get('why_they_qualify', 'N/A')}")
        
        print()
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo()

