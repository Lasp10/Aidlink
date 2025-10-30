#!/usr/bin/env python3
"""
Netlify Function: Status check
"""

import json
import os
import sys
from datetime import datetime

def handler(event, context):
    """Netlify serverless function handler"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Check API availability
        google_places_available = bool(os.getenv('GOOGLE_PLACES_API_KEY'))
        gemini_available = bool(os.getenv('GEMINI_API_KEY'))
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'running',
                'data_source': 'netlify_functions',
                'google_places_available': google_places_available,
                'gemini_available': gemini_available,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

