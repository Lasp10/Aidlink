#!/usr/bin/env python3
"""
AidLink Local Dev Server (Flask)

Purpose
- Let you run the app locally while production runs on Netlify Functions

Usage
- pip install flask flask-cors python-dotenv requests google-generativeai
- python3 dynamic_app.py
- Open http://localhost:8000
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
from pathlib import Path

# Load env if present (safe default for production)
ENV_FILE = os.getenv('AIDLINK_ENV_FILE', 'aidlink.env')
env_path = Path(ENV_FILE)
if env_path.exists():
    load_dotenv(env_path)

# Import local modules - use relative imports when imported as package,
# or direct imports when run directly
try:
    # Try relative imports first (when imported as AIDLINK.dynamic_app)
    from .google_places_client import GooglePlacesClient
    from .openstreetmap_community_client import OSMCommunityClient
    from .ai_eligibility_assistant import AIEligibilityAssistant
    from .demo_211_data import get_demo_211_data
except ImportError:
    # Fallback to direct imports (when run directly)
    from google_places_client import GooglePlacesClient
    from openstreetmap_community_client import OSMCommunityClient
    from ai_eligibility_assistant import AIEligibilityAssistant
    from demo_211_data import get_demo_211_data


app = Flask(__name__, static_folder=None)
CORS(app)


@app.route('/')
def index():
    # Serve the same frontend as Netlify (root index.html)
    # Look for index.html in parent directory (root of project)
    # Get the absolute path to the project root
    current_file = Path(__file__).resolve()
    
    # Try multiple possible locations for index.html
    possible_paths = [
        current_file.parent.parent / 'index.html',  # Go up from AIDLINK/ to root
        Path.cwd() / 'index.html',  # Current working directory
        Path.cwd().parent / 'index.html',  # Parent of CWD
        Path('/opt/render/project/src/index.html'),  # Render's project root
        Path('index.html'),  # Relative to current directory
    ]
    
    # Try each path
    for index_path in possible_paths:
        if index_path.exists():
            return send_file(str(index_path))
    
    # If none found, return error with debug info
    return jsonify({
        'error': 'index.html not found',
        'searched_paths': [str(p) for p in possible_paths],
        'current_file': str(current_file),
        'cwd': str(Path.cwd())
    }), 500


@app.route('/api/status')
def status():
    google_places_available = bool(os.getenv('GOOGLE_PLACES_API_KEY'))
    gemini_available = bool(os.getenv('GEMINI_API_KEY'))
    return jsonify({
        'status': 'running',
        'data_source': 'local_flask',
        'google_places_available': google_places_available,
        'gemini_available': gemini_available,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json() or {}
        query = (data.get('query') or '').strip()
        location = (data.get('location') or 'Sacramento, CA').strip()
        category = (data.get('category') or 'general').strip()
        max_results = int(data.get('max_results') or 10)
        radius = int(data.get('radius') or 10)

        google_places = GooglePlacesClient()
        if google_places and getattr(google_places, 'available', False):
            res = google_places.search_places(query, location, category, max_results, radius_miles=radius)
            if res.get('success') and res.get('recommendations'):
                return jsonify(res)

        osm = OSMCommunityClient()
        if osm and getattr(osm, 'available', True):
            res = osm.search_places(query, location, category, max_results)
            if res.get('success') and res.get('recommendations'):
                return jsonify(res)

        # Fallback demo
        demo = get_demo_211_data(query, location, category, max_results)
        resources = []
        for i, r in enumerate(demo or []):
            resources.append({
                'id': f'verified_{i+1:03d}',
                'name': r.get('name'),
                'description': r.get('description'),
                'category': category,
                'address': r.get('address'),
                'phone': r.get('phone'),
                'website': r.get('website'),
                'hours': r.get('hours'),
                'services': r.get('services'),
                'verified': True,
                'source': 'verified_sacramento'
            })
        return jsonify({
            'success': True,
            'query': query,
            'recommendations': resources,
            'total_results': len(resources),
            'confidence': 0.95,
            'source': 'verified_sacramento_resources'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-eligibility', methods=['POST'])
def analyze_eligibility():
    try:
        data = request.get_json() or {}
        situation = (data.get('situation') or '').strip()
        resources_found = data.get('resources') or []
        location = data.get('location')

        if not situation:
            return jsonify({'error': 'Situation description is required'}), 400

        assistant = AIEligibilityAssistant()
        if not getattr(assistant, 'available', False):
            # Graceful fallback if Gemini not configured
            analysis = assistant._fallback_analysis(situation)
            plan = assistant._get_immediate_action_plan(analysis, location)
            checklist = assistant._basic_document_checklist(analysis)
            return jsonify({
                'success': True,
                'analysis': analysis.get('analysis', {}),
                'action_plan': plan.get('action_plan', {}),
                'document_checklist': checklist,
                'ai_model': 'simple_fallback'
            })

        analysis = assistant.analyze_user_situation(situation)
        if resources_found:
            plan = assistant.create_action_plan_from_resources(analysis, resources_found, location)
        else:
            plan = assistant.create_action_plan(analysis, location)
        checklist = assistant.generate_document_checklist(analysis, plan)
        return jsonify({
            'success': True,
            'analysis': analysis.get('analysis', {}),
            'action_plan': plan.get('action_plan', {}),
            'document_checklist': checklist,
            'ai_model': 'gemini-pro'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    port = int(os.getenv('PORT', 8000))
    # Disable debug in production (set DEBUG=False in environment)
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()


