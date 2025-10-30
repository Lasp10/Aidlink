#!/usr/bin/env python3
"""
Netlify Function: Analyze eligibility
"""

import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai_eligibility_assistant import AIEligibilityAssistant

def handler(event, context):
    """Netlify serverless function handler"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('situation', '').strip()
        resources_found = body.get('resources', [])
        location = body.get('location')
        
        if not user_input:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Situation description is required'})
            }
        
        eligibility_assistant = AIEligibilityAssistant()
        
        if not eligibility_assistant.available:
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': 'AI Eligibility Assistant not available'
                })
            }
        
        analysis = eligibility_assistant.analyze_user_situation(user_input)
        
        # Get action plan
        if resources_found and len(resources_found) > 0:
            action_plan = eligibility_assistant.create_action_plan_from_resources(
                analysis,
                resources_found,
                location=location
            )
        else:
            action_plan = eligibility_assistant.create_action_plan(analysis, location=location)
        
        # Generate document checklist
        document_checklist = eligibility_assistant.generate_document_checklist(analysis, action_plan)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'analysis': analysis.get('analysis', {}),
                'action_plan': action_plan.get('action_plan', {}),
                'document_checklist': document_checklist,
                'ai_model': 'gemini-pro'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

