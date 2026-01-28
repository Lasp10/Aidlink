# AidLink Project Structure - Complete File Explanation

## 📁 Project Overview
AidLink is an AI-powered community resource navigator that helps people find local assistance programs (food, housing, healthcare, employment, financial aid). It combines multiple data sources (Google Places, OpenStreetMap, verified Sacramento data) with AI (Google Gemini) to provide personalized eligibility analysis and action plans.

---

## 🗂️ Root Directory Files

### 1. `dynamic_app.py` (Root)
**Purpose**: Local Flask development server entry point  
**Key Features**:
- **Environment Loading**: Automatically finds and loads `aidlink.env` from root or `AIDLINK/` folder
- **Path Management**: Adds `AIDLINK/` to Python path so modules can be imported
- **Routes**:
  - `GET /` - Serves `index.html` frontend
  - `GET /api/status` - Health check showing API availability
  - `POST /api/search` - Main search endpoint (tries Google Places → OSM → fallback demo data)
  - `POST /api/analyze-eligibility` - AI-powered eligibility analysis using Gemini
- **Fallback Chain**: Google Places → OpenStreetMap → Demo Sacramento data
- **Port**: Defaults to 8000, configurable via `PORT` env variable

**Important**: This is the file you run locally (`python dynamic_app.py`) for development.

---

### 2. `index.html` (Root)
**Purpose**: Single-page application frontend  
**Key Features**:
- **Modern UI**: Dark theme with gradient backgrounds, Poppins font
- **Search Form**: Query input, location, radius selector (5-25 miles)
- **Emergency Button**: Floating red button (bottom-right) for 211/988 crisis lines
- **Results Display**: Cards showing resources with distance, rating, transportation info
- **AI Eligibility Analysis**: Modal showing personalized action plans and document checklists
- **Progressive Web App**: Includes service worker (`sw.js`) for offline capability
- **Responsive Design**: Works on mobile and desktop

**Important Sections**:
- Emergency banner at top (211/988)
- Search form with location autocomplete
- Results grid with resource cards
- Eligibility analysis modal
- Floating emergency button

---

### 3. `requirements.txt` (Root)
**Purpose**: Python dependencies for Flask deployment  
**Contents**:
- `flask==2.3.3` - Web framework
- `flask-cors==4.0.0` - Cross-origin resource sharing
- `python-dotenv==1.0.0` - Environment variable management
- `requests==2.31.0` - HTTP client for API calls
- `google-generativeai==0.3.2` - Google Gemini AI SDK
- `gunicorn==21.2.0` - Production WSGI server

**Usage**: `pip install -r requirements.txt`

---

### 4. `runtime.txt` (Root)
**Purpose**: Specifies Python version for deployment platforms  
**Contents**: `python-3.11.9`

**Note**: Used by platforms like Heroku, Railway (now removed), etc.

---

### 5. `Dockerfile` (Root)
**Purpose**: Docker container configuration for production deployment  
**Key Steps**:
1. Uses Python 3.11 slim base image
2. Sets working directory to `/app`
3. Copies `AIDLINK/requirements.txt` and installs dependencies
4. Copies entire `AIDLINK/` folder into container
5. Sets `PORT=8000` environment variable
6. Runs `gunicorn` production server

**Usage**: `docker build -t aidlink . && docker run -p 8000:8000 aidlink`

---

### 6. `.dockerignore`
**Purpose**: Excludes files from Docker build context  
**Excludes**:
- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `aidlink.env` - Environment secrets (should be injected at runtime)
- `data/` - Local database files

**Why Important**: Keeps Docker images small and secure (no secrets in image)

---

### 7. `aidlink.env.example`
**Purpose**: Template showing required environment variables  
**Key Variables**:
- `GOOGLE_PLACES_API_KEY` - For Google Places API (real-time location data)
- `GEMINI_API_KEY` - For Google Gemini AI (eligibility analysis)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Development mode flag

**Usage**: Copy to `aidlink.env` and fill in your actual keys.

---

## 📁 AIDLINK/ Directory (Core Application)

### 8. `AIDLINK/dynamic_app.py`
**Purpose**: Core Flask application (used by both root and Docker)  
**Differences from Root**:
- Simpler path handling (assumes it's already in the right directory)
- Direct imports (no path manipulation needed)
- Same routes and functionality

**Note**: This is the version used when deployed in Docker or when running from `AIDLINK/` directory.

---

### 9. `AIDLINK/google_places_client.py` ⭐ **CRITICAL**
**Purpose**: Google Places API integration for real-time community resource search  
**Key Features**:

**Initialization**:
- Reads `GOOGLE_PLACES_API_KEY` from environment
- Sets `available` flag based on API key presence
- Base URL: `https://maps.googleapis.com/maps/api/place`

**Main Method: `search_places()`**:
1. **Geocoding**: Converts location string (e.g., "Sacramento, CA") to lat/lng coordinates
2. **Query Enhancement**: Adds category-specific keywords (food bank, shelter, etc.)
3. **Text Search**: Uses Places API Text Search (better for keywords than Nearby Search)
4. **Place Details**: Fetches detailed info for each place (hours, phone, website, rating)
5. **Distance Calculation**: Uses Haversine formula to calculate real distance in miles
6. **Ranking Algorithm**: Scores resources by:
   - Rating (0-60 points) - **HIGHEST WEIGHT**
   - Distance (0-25 points) - Closer is better
   - Relevance (0-15 points) - Keyword matching
7. **Filtering**: Removes resources beyond user's selected radius
8. **Transportation Info**: Generates helpful transportation guidance based on distance

**Fallback**: If API fails or unavailable, falls back to `demo_211_data.py`

**Important Methods**:
- `_geocode_location()` - Converts address to coordinates
- `_search_nearby_places()` - Text search with radius
- `_get_place_details()` - Detailed place information
- `_calculate_distance()` - Haversine distance calculation
- `_rank_resources()` - Intelligent ranking algorithm
- `_get_transportation_info()` - Generates transportation guidance

**Cost**: Google Places API has $200/month free credit, then pay-as-you-go.

---

### 10. `AIDLINK/openstreetmap_community_client.py` ⭐ **FREE ALTERNATIVE**
**Purpose**: OpenStreetMap Overpass API integration (100% free, unlimited)  
**Key Features**:

**Initialization**:
- Always available (no API key needed!)
- Uses Overpass API: `https://overpass-api.de/api/interpreter`
- Uses Nominatim for geocoding (also free)

**Main Method: `search_places()`**:
1. **Tag Mapping**: Maps categories to OSM tags (e.g., `amenity=food_bank`, `amenity=shelter`)
2. **Geocoding**: Uses Nominatim to get coordinates
3. **Overpass Query**: Builds Overpass QL query to search within bounding box
4. **Result Processing**: Extracts name, address, phone, website from OSM tags
5. **Formatting**: Converts OSM data to AidLink resource format

**Advantages**:
- ✅ 100% free, no API key needed
- ✅ Unlimited requests
- ✅ Community-maintained data

**Disadvantages**:
- ⚠️ Less detailed than Google Places (no ratings, fewer hours)
- ⚠️ May have incomplete data in some areas

**Fallback**: Falls back to `demo_211_data.py` if no results found.

---

### 11. `AIDLINK/ai_eligibility_assistant.py` ⭐ **AI POWERED**
**Purpose**: Google Gemini AI integration for eligibility analysis and action planning  
**Key Features**:

**Initialization**:
- Reads `GEMINI_API_KEY` from environment
- Uses `gemini-2.5-flash` model
- Falls back to simple rule-based analysis if API unavailable

**Main Methods**:

**1. `analyze_user_situation(user_input)`**:
- Takes natural language description (e.g., "I'm homeless with 2 kids")
- Uses Gemini to extract:
  - Situation summary
  - Key factors (homeless, unemployed, has_children, etc.)
  - Likely eligible programs with confidence scores
  - Urgency score (1-10)
  - Barriers and solutions
- Returns comprehensive JSON analysis

**2. `create_action_plan_from_resources(analysis, resources, location)`**:
- Creates **SHORT** action plan (2-3 steps max) using actual resources found
- Includes specific phone numbers, addresses, timeframes
- Prioritizes resources with transportation assistance or closer distances
- Uses Gemini to generate personalized, actionable steps

**3. `create_action_plan(analysis, location)`**:
- Creates action plan when no resources found yet
- Includes immediate actions (today), this week, this month
- Provides encouragement and timeline

**4. `generate_document_checklist(analysis, action_plan)`**:
- Generates personalized list of documents needed
- Based on user's situation and programs they're applying for
- Common docs: ID, SSN, proof of income, proof of residence, birth certificates

**5. `suggest_followup_questions(current_situation)`**:
- Generates intelligent follow-up questions to better understand user
- Uses Gemini to create contextual questions

**6. `translate_government_jargon(text)`**:
- Translates complex eligibility requirements into plain English
- Helps users understand what programs actually require

**7. `identify_barriers(situation, resources)`**:
- Identifies potential obstacles (transportation, documentation, language, etc.)
- Suggests solutions for each barrier

**Fallback Methods**:
- `_fallback_analysis()` - Simple keyword extraction
- `_get_immediate_action_plan()` - Basic 211 referral
- `_basic_document_checklist()` - Standard document list

**Cost**: Google Gemini API has free tier, then pay-as-you-go.

---

### 12. `AIDLINK/demo_211_data.py` ⭐ **FALLBACK DATA**
**Purpose**: Verified Sacramento community resources (fallback when APIs unavailable)  
**Key Features**:

**Main Function: `get_demo_211_data(query, location, category, max_results)`**:
- Returns hardcoded list of **REAL** Sacramento-area organizations
- Categories: food, housing, employment, healthcare, financial
- Each resource includes:
  - Name, description, address, phone, website
  - Hours, services, eligibility requirements
  - Latitude/longitude coordinates

**Real Organizations Included**:
- **Food**: Sacramento Food Bank, Placer Food Bank, Loaves & Fishes
- **Housing**: SHRA, Wind Youth Services, Salvation Army
- **Employment**: Sacramento Works, Goodwill, EDD
- **Healthcare**: Sacramento County Health Center, WellSpace Health, UC Davis
- **Financial**: Sacramento Credit Union, CDSS, County Human Assistance

**Usage**: Used as fallback when:
- Google Places API unavailable or fails
- OpenStreetMap returns no results
- User wants to test without API keys

**Note**: These are real organizations, but data is static (not live).

---

### 13. `AIDLINK/requirements.txt`
**Purpose**: Same as root `requirements.txt` - Python dependencies  
**Note**: Duplicated for Docker builds that copy from `AIDLINK/` folder.

---

### 14. `AIDLINK/runtime.txt`
**Purpose**: Same as root - Python version specification  
**Note**: Duplicated for consistency.

---

### 15. `AIDLINK/Dockerfile`
**Purpose**: Alternative Dockerfile (simpler, assumes files are in current directory)  
**Differences from Root Dockerfile**:
- Copies `requirements.txt` from current directory (not `AIDLINK/`)
- Copies all files from current directory (not `AIDLINK/`)

**Usage**: Run from `AIDLINK/` directory if you want this version.

---

### 16. `AIDLINK/aidlink.env` & `aidlink.env.example`
**Purpose**: 
- `aidlink.env` - **ACTUAL** environment variables (contains secrets, should be gitignored)
- `aidlink.env.example` - Template showing what variables are needed

**Important**: Never commit `aidlink.env` to git! It contains API keys.

---

### 17. `AIDLINK/data/aidlink.db`
**Purpose**: SQLite database (if used for caching/storage)  
**Note**: Currently not heavily used, but structure exists for future data persistence.

---

### 18. `AIDLINK/static/` Directory
**Purpose**: Static assets for Progressive Web App (PWA)

**Files**:
- `icon-192.png` & `icon-512.png` - App icons for mobile home screen
- `manifest.json` - PWA manifest (app name, colors, display mode)
- `sw.js` - Service worker for offline functionality

**manifest.json**:
- Defines app as "AidLink - Find Help Near You"
- Sets theme colors (purple gradient)
- Specifies icons for mobile installation
- Enables standalone display mode (feels like native app)

---

## 🔄 How Files Work Together

### Request Flow:
1. **User visits** `http://localhost:8000/`
2. **`dynamic_app.py`** serves `index.html`
3. **User searches** for "food assistance in Sacramento"
4. **Frontend** sends `POST /api/search` with query, location, radius
5. **`dynamic_app.py`** route handler:
   - Tries `GooglePlacesClient.search_places()` first
   - If fails/unavailable → tries `OSMCommunityClient.search_places()`
   - If fails → uses `get_demo_211_data()` fallback
6. **Results returned** to frontend, displayed as cards
7. **User clicks "Analyze Eligibility"**
8. **Frontend** sends `POST /api/analyze-eligibility` with situation description
9. **`dynamic_app.py`** uses `AIEligibilityAssistant`:
   - `analyze_user_situation()` - Understands their needs
   - `create_action_plan_from_resources()` - Creates personalized plan
   - `generate_document_checklist()` - Lists required documents
10. **AI analysis returned** to frontend, displayed in modal

### Data Source Priority:
1. **Google Places** (if API key configured) - Best quality, real-time, ratings
2. **OpenStreetMap** (always available) - Free, community data
3. **Demo Sacramento Data** (fallback) - Static but verified resources

---

## 🔑 Environment Variables Required

### Required for Full Functionality:
- `GOOGLE_PLACES_API_KEY` - For real-time location search
- `GEMINI_API_KEY` - For AI eligibility analysis

### Optional:
- `PORT` - Server port (default: 8000)
- `DEBUG` - Development mode (default: True)

### How to Set:
1. Copy `aidlink.env.example` to `aidlink.env`
2. Fill in your API keys
3. File is automatically loaded by `dynamic_app.py`

---

## 🚀 Running the Application

### Local Development:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment (copy example and add keys)
cp aidlink.env.example aidlink.env
# Edit aidlink.env with your keys

# Run Flask server
python dynamic_app.py

# Visit http://localhost:8000
```

### Docker Deployment:
```bash
# Build image
docker build -t aidlink .

# Run container (with env vars)
docker run -p 8000:8000 \
  -e GOOGLE_PLACES_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  aidlink
```

---

## 📊 Key Algorithms & Logic

### 1. Resource Ranking (Google Places):
- **Rating Score**: 0-60 points (5.0 rating = 60 points)
- **Distance Score**: 0-25 points (closer = better)
- **Relevance Score**: 0-15 points (keyword matches)
- **Final Sort**: Rating first, then total score, then distance

### 2. Distance Calculation:
- Uses **Haversine formula** for accurate Earth surface distance
- Converts to miles
- Accounts for Earth's curvature

### 3. Transportation Guidance:
- **≤0.5 miles**: "Walkable (~10 min walk)"
- **≤1 mile**: "Walkable or short bus ride"
- **≤3 miles**: "Short bus trip or ride share ($X-$Y)"
- **>3 miles**: "Call for transportation assistance or ride share"

### 4. AI Prompt Engineering:
- Uses structured JSON prompts for consistent output
- Includes examples in prompts for better results
- Extracts JSON from AI responses (handles markdown formatting)

---

## 🎯 Important Design Decisions

1. **Multiple Data Sources**: Ensures app works even if one API fails
2. **Graceful Degradation**: Falls back to simpler methods if AI unavailable
3. **Short Action Plans**: Limits to 2-3 steps to avoid overwhelming users
4. **Real Distance**: Calculates actual distance, not API estimates
5. **Rating Priority**: Favors highly-rated resources over closer ones
6. **Transportation Focus**: Provides practical guidance for accessing resources

---

## 🔒 Security Notes

1. **Never commit `aidlink.env`** - Contains API keys
2. **Use `.dockerignore`** - Prevents secrets in Docker images
3. **Environment variables** - Inject at runtime, not build time
4. **CORS enabled** - Allows frontend to call API (configure for production)

---

## 📝 Summary

**AidLink** is a comprehensive community resource finder that:
- ✅ Searches multiple data sources (Google Places, OSM, verified data)
- ✅ Uses AI to understand user needs and create action plans
- ✅ Provides practical transportation guidance
- ✅ Works offline with fallback data
- ✅ Prioritizes quality resources (ratings) over proximity
- ✅ Generates personalized document checklists
- ✅ Identifies barriers and suggests solutions

The architecture is modular, with clear separation between:
- **Frontend** (`index.html`) - User interface
- **Backend** (`dynamic_app.py`) - API routes
- **Data Sources** (`google_places_client.py`, `openstreetmap_community_client.py`, `demo_211_data.py`)
- **AI** (`ai_eligibility_assistant.py`) - Eligibility analysis

Each component can work independently, ensuring the app functions even if some services are unavailable.

