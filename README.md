# 2D Game Asset Generator

AI-powered 2D game asset generation tool! Create characters, backgrounds, items, and all the assets you need for 2D games using Google's Gemini AI models.

- Live Demo: https://sprite-studio.com/
- Play Game Here: https://gd.games/games/feac74c4-ee1a-4858-949b-bea628e5a081
- LinkedIn: https://www.linkedin.com/in/jianleee/
- More Detail: https://www.linkedin.com/posts/jianleee_indie-and-solo-game-developers-often-spend-activity-7409553353351032833-IhEY?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEuJUtMBpdDPXXm7UTo9Z0abB5vcvXUFdxA

## 🏗️ Architecture

### Hybrid Architecture

This project implements a unique hybrid architecture that leverages the strengths of multiple frameworks:

- **Next.js Frontend** (`frontend/`): Modern React-based dashboard with authentication, token management, and user interface
- **FastAPI Backend** (`backend/api_server.py`): RESTful API for profile management, token operations, and image generation endpoints
- **Gradio Interface** (`backend/game_asset_app.py`): Embedded iframe-based generation studio with rich UI components
- **Supabase**: Authentication, database (PostgreSQL), and file storage
- **AWS Infrastructure**: Amplify (frontend hosting), EC2 (backend hosting), Route 53 (DNS)

### Architecture Flow

1. User authenticates via Next.js frontend using Supabase Auth (Google OAuth supported)
2. JWT token is passed to Gradio iframe via URL query string (`?token=...`)
3. Gradio auto-login extracts token from URL and validates with Supabase
4. Token balance is polled every 5 seconds via FastAPI `/profile` endpoint
5. Image generation consumes tokens and updates balance in real-time
6. Generated images are stored in Supabase Storage and metadata saved to PostgreSQL

### Key Design Decisions

- **Token-based Billing**: Each image generation consumes 1 token. New users start with 10 tokens.
- **Real-time Updates**: 5-second polling ensures token balance reflects immediately after generation
- **Session Sharing**: JWT tokens shared between Next.js and Gradio via URL parameters
- **Security**: API keys never logged, CORS properly configured, environment variables secured

## 🚀 Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Supabase Client** (authentication)

### Backend
- **FastAPI** (REST API)
- **Gradio 5.44+** (generation interface)
- **Python 3.11+**
- **Supabase Python Client** (database, storage, auth validation)

### Infrastructure
- **AWS Amplify** (frontend hosting, CI/CD)
- **AWS EC2** (backend hosting)
- **AWS Route 53** (DNS management)
- **Supabase** (PostgreSQL, Storage, Auth)

### AI/ML
- **Google Gemini API** (image generation)
- **Gemini 2.5 Flash Image Preview** (model)





## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Google Gemini API key
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HenryKang1/Sprite_generator1.git
   cd Sprite_generator
   ```

2. **Install dependencies**
   ```bash
   # Using UV (recommended)
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   # Method 1: Copy .env_example file (Recommended)
   copy .env_example .env
   
   # Method 2: Create .env file directly
   cat <<'EOF' > .env
   GEMINI_API_KEY=your_gemini_api_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   EOF
   ```
   
   **Important**: replace the values with your real keys before running the app.

4. **Run the Gradio interface (optional legacy UI)**
   ```bash
   uv run python -m backend.game_asset_app
   ```

5. **Access the interface**
   Open your browser and navigate to `http://localhost:7861`

## 📖 Usage Guide

### 👤 **Character Generation**

1. Enter character description in the text area
2. Select style preferences (optional)
3. Upload reference image (optional)
4. Click "Generate Character" button

## Key Features

### Token Management
- Initial Tokens: New users receive 10 tokens upon signup
- Real-time Updates: Token balance updates every 5 seconds via FastAPI polling
- Auto-deduction: Tokens automatically consumed on image generation
- Low Token Warning: Upgrade modal appears when tokens ≤ 10
### Image Generation
- Character Generation: Create unique characters with style customization
- Sprite Animation: Generate animated sprite sheets (walk, run, jump, attack, etc.)
- Background Design: Create immersive game backgrounds
- Item Generation: Generate weapons, armor, potions, and game items
- Pixel Art Mode: Toggle for retro-style pixel art generation
### User Experience
- Google OAuth: One-click sign-in with Google
- Session Persistence: JWT tokens maintain authentication across page reloads
- Responsive Design: Modern UI with Tailwind CSS
- Real-time Feedback: Loading states and error handling

# Development Journey
## Major Challenges Solved
### 1. Hybrid Architecture Integration
- Implemented JWT token sharing between Next.js and Gradio via URL query strings
- Resolved cross-origin communication issues
- Optimized token synchronization (moved from postMessage to FastAPI polling)
### 2. Production Deployment
- Configured AWS Amplify for Next.js SSR deployment
- Set up EC2 instance with proper security groups
- Resolved CORS issues by adding Amplify URL to allowed origins
- Implemented service restart procedures
### 3. Security Issues
- Identified and fixed API key exposure in logs
- Removed sensitive data from console output
- Implemented proper environment variable handling
### 4. Database Schema
- Created Supabase tables: user_tokens, user_projects, generated_images
- Implemented Row Level Security (RLS) policies
- Fixed missing table errors in production
### 5. Real-time Token Updates
- Implemented 5-second polling for token balance
- Added proper error handling and loading states
- Ensured UI reflects token changes immediately after generation
### 6. Image Generation Debugging
- Added comprehensive logging for generation pipeline
- Fixed JavaScript token extraction in Gradio auto-login
- Resolved API key permission issues


## 🏗️ Project Structure

```
sprite-studio/
├── backend/
│   ├── api_server.py              # FastAPI REST API
│   ├── game_asset_app.py          # Gradio generation interface
│   ├── game_asset_generator.py    # Core generation logic
│   ├── pixel_character_generator.py
│   ├── supabase_client.py         # Supabase helpers (auth/tokens/storage)
│   ├── config_manager.py          # Configuration management
│   ├── gradio_*.py                # Gradio UI components
│   └── utils.py                   # Shared utilities
├── frontend/
│   ├── app/                       # Next.js App Router
│   │   ├── studio/               # Studio page with Gradio iframe
│   │   └── page.tsx              # Landing page
│   ├── components/               # React components
│   │   └── Header.tsx            # Header with token display
│   └── lib/                      # Utilities
│       └── supabase.ts           # Supabase client
├── supabase_schema.sql            # Database schema
├── pyproject.toml                # Python dependencies
└── README.md
```



## 🔐 Supabase Auth & Storage Blueprint

- `supabase_client.py`: loads env vars, creates a singleton service-role client, validates JWTs, and handles storage uploads for the Gradio backend.
- `frontend/lib/supabase.ts`: browser-safe client that uses only the anon key for sign-up/log-in flows in Next.js.

### Recommended Tables

| Table | Columns | Purpose |
| --- | --- | --- |
| `user_projects` | `id (uuid)`, `user_id`, `project_name`, `created_at` | Logical grouping for a user’s characters/items/backgrounds. |
| `generated_images` | `id (uuid)`, `user_id`, `project_id`, `image_type`, `image_url`, `metadata (jsonb)`, `created_at` | Stores metadata and Supabase Storage URLs for generated assets. |

Suggested Supabase Storage layout:

```
generated/
  <user_id>/
    <project_id>/
      character.png
      sprite_attack_frame1.png
```

### Token / Request Flow

1. **Next.js** handles `signUp` and `signInWithPassword` using the anon client and stores the session tokens.
2. **Frontend requests** to Gradio include `Authorization: Bearer <access_token>` from `supabase.auth.getSession()`.
3. **Gradio** calls `validate_access_token` from `supabase_client.py` to resolve the `user_id`.
4. **Backend** writes rows into `user_projects` / `generated_images` and uploads resulting images to the `generated` bucket using the service-role key.

## 🧱 Hybrid Architecture (Next.js + Gradio)

- **Next.js Dashboard** (`frontend/`): Login, account management, and dashboard UI
- **Gradio Studio** (`backend/game_asset_app.py`): Full-featured sprite generation tool
- **FastAPI Backend** (`backend/api_server.py`): REST API for Next.js (optional, for future use)

### Architecture Flow

1. User logs in at `http://localhost:3000` (Next.js)
2. Dashboard shows token count and "Open Sprite Studio" button
3. Clicking the button navigates to `/studio` (same window, no popup)
4. Gradio UI loads in an iframe with token passed via query string
5. Token updates are synchronized via `postMessage` between iframe and parent

### Running locally

**Option 1: Full Stack (Recommended for development)**

```bash
# Terminal 1: Gradio UI
cd /Users/jlee/4-1/Sprite/bug_Sprite_generator1-feature-ui-tabs-update
uv sync
uv run python -m backend.game_asset_app
# Access at http://localhost:7861

# Terminal 2: FastAPI Backend (optional, for Next.js API calls)
uv run python -m uvicorn backend.api_server:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Next.js Frontend
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

**Option 2: Gradio Only (Legacy)**

```bash
cd /Users/jlee/4-1/Sprite/bug_Sprite_generator1-feature-ui-tabs-update
uv sync
uv run python -m backend.game_asset_app
# Access at http://localhost:7861
```

### Environment Variables

**Backend (.env):**
```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

**Frontend (frontend/.env.local):**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_GRADIO_URL=http://localhost:7861
```

## 🛠️ Configuration

### Environment Variables

Create a backend `.env` and frontend `.env.local` and set the following variables:

```env
# .env (Python / Gradio backend)
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key  # backend-only
OUTPUT_DIR=data/output
IMAGE_MODEL_NAME=gemini-2.5-flash-image-preview
```

```env
# frontend/.env.local (Next.js)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### API Setup

1. **Get Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## Deployment

### AWS Amplify (Frontend)
1. Connect GitHub repository to Amplify
2. Configure build settings:
```
      version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend && npm install
       build:
         commands:
           - cd frontend && npm run build
     artifacts:
       baseDirectory: frontend/.next
       files:
         - '**/*'
```
4. Set environment variables in Amplify Console
5. Deploy

### AWS EC2 (Backend)
1. Launch EC2 instance (t3.micro recommended)
2. SSH into instance
```
   ssh -i your-key.pem ubuntu@your-ec2-ip
```
4.  Clone repository and setup:
```
   git clone https://github.com/JLeeq/sprite-studio.git
   cd sprite-studio
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
4. Start services:
```
   # FastAPI
   nohup python -m uvicorn backend.api_server:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
   
   # Gradio
   nohup python -m backend.game_asset_app > /tmp/gradio.log 2>&1 &
```
5. Configure security groups (ports 8000, 7861)
6. Set up Elastic IP and Route 53 DNS



## 🎨 Style Options

Choose from various art styles, moods, color palettes, character styles, and composition options to create unique game assets:

- **Art Styles**: Traditional Manga/Anime, Shonen, Shoujo, Seinen, Chibi, Cyberpunk, Fantasy, Horror, etc.
- **Moods**: Epic, Dark/Mysterious, Light/Cheerful, Dramatic, Action-packed, etc.
- **Color Palettes**: Full Color, Black & White, Sepia, Monochromatic, Warm Tones, Cool Tones, etc.
- **Character Styles**: Detailed/Realistic, Stylized/Expressive, Simple/Clean, etc.

## 🔧 Advanced Features

- **Smart Prompts**: Generate optimized prompts while maintaining character consistency
- **Reference Images**: Upload reference images to guide style, composition, and character appearance
- **Configuration Management**: Save and reuse frequently used style settings
- **Batch Generation**: Generate multiple action sprites at once

## 📋 Usage Examples

You can use this tool to generate game assets for various game types:

1. **RPG Games**: Warriors, mages, archers, and their weapons and armor
2. **Platformer Games**: Action sprites for jumping, running, attacking, etc.
3. **Puzzle Games**: Various items and background elements
4. **Adventure Games**: Environmental backgrounds and interactive objects

## Troubleshooting
### 1. CORS Errors
- Ensure Amplify URL is in backend/api_server.py allowed origins
- Check FastAPI CORS middleware configuration
### 2. Token Not Updating
- Verify FastAPI /profile endpoint is accessible
- Check browser console for fetch errors
- Confirm 5-second polling is active
### 3. Image Generation Fails
- Check API key is valid and not leaked
- Verify Gemini API quota
- Check EC2 logs: tail -f /tmp/gradio.log
### 4. Database Errors
- Run supabase_schema.sql in Supabase Dashboard
- Verify RLS policies are enabled

## 🙏 Acknowledgments

- Google Gemini AI models
- Gradio team
- All contributors

*Transform your imagination into 2D game assets with the power of AI!*
