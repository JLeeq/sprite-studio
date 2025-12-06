# 2D Game Asset Generator 🎮✨

AI-powered 2D game asset generation tool! Create characters, backgrounds, items, and all the assets you need for 2D games using Google's Gemini AI models.

## 🌟 Key Features

- **🎨 AI-Powered Generation**: Automatically generate characters, backgrounds, and items with AI
- **🎭 Style Customization**: Various art styles, moods, color palettes, and composition options
- **🏃 Sprite Generation**: Batch generate multiple action sprites for characters
- **⚙️ Configuration Management**: Save and reuse frequently used style settings
- **🖼️ Reference Images**: Upload reference images for consistent character design
- **🖥️ Web Interface**: User-friendly Gradio interface

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

### 🏃 **Character Sprite Generation**

1. Enter character description
2. Enter action list separated by commas (e.g., idle, walk, run, jump)
3. Select style preferences
4. Click "Generate Sprites" button

### 🌄 **Background Generation**

1. Enter background description
2. Select orientation (landscape/portrait)
3. Select style preferences
4. Click "Generate Background" button

### 🎒 **Item Generation**

1. Enter item description
2. Select style preferences
3. Upload reference image (optional)
4. Click "Generate Item" button

### ⚙️ **Configuration Management**

1. Save frequently used style settings
2. Load and reuse saved settings
3. Delete unnecessary settings

## 🏗️ Project Structure

```
Sprite_generator/
├── backend/
│   ├── api_server.py            # FastAPI endpoints (Next.js consumes these)
│   ├── game_asset_app.py        # Legacy Gradio interface
│   ├── game_asset_generator.py  # Core game asset generation logic
│   ├── pixel_character_generator.py
│   ├── supabase_client.py       # Supabase helpers (auth/tokens/storage)
│   ├── config_manager.py        # Configuration management module
│   └── utils.py                 # Shared style data/constants
├── frontend/                    # Next.js application
├── pyproject.toml               # Project configuration
├── .env                         # Environment variables (create this)
├── data/
│   ├── output/                  # Generated assets
│   │   ├── characters/          # Character images
│   │   ├── backgrounds/         # Background images
│   │   ├── items/               # Item images
│   │   └── references/          # Reference images
│   ├── configs/                 # Saved configurations
│   │   └── saved_configs.json
│   └── examples/                # Example files
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

## 🤝 Contributing

If you'd like to contribute to this project:

1. Fork this repository
2. Create a new feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more details.

## 🙏 Acknowledgments

- Google Gemini AI models
- Gradio team
- All contributors

*Transform your imagination into 2D game assets with the power of AI!*