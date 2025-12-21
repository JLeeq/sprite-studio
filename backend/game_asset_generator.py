"""
2D 게임 어셋 생성 툴 - 나노바나나 API 활용
"""

import os
import PIL
from io import BytesIO
from google import genai
from dotenv import load_dotenv
import pathlib
import time
import shutil
from PIL import Image
from .utils import ART_STYLES, MOOD_OPTIONS, COLOR_PALETTES, CHARACTER_STYLES, LINE_STYLES, COMPOSITION_STYLES

# Load environment variables
load_dotenv()

class GameAssetGenerator:
    def __init__(self):
        """Initialize the game asset generator with API clients and configuration."""
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required but not found.")

        # API key loaded (not logging to prevent leaks)

        self.output_dir = os.getenv("OUTPUT_DIR", "data/output")
        self.character_dir = os.path.join(self.output_dir, "characters")
        self.background_dir = os.path.join(self.output_dir, "backgrounds")
        self.item_dir = os.path.join(self.output_dir, "items")
        self.reference_dir = os.path.join(self.output_dir, "references")

        self.image_gen_model_name = os.getenv("IMAGE_MODEL_NAME", "gemini-2.5-flash-image-preview")

        # Initialize Gemini client
        print("🔄 Initializing Gemini clients...")
        self.image_gen_client = genai.Client(api_key=self.api_key)
        print("✅ Gemini clients initialized successfully")

        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.character_dir, exist_ok=True)
        os.makedirs(self.background_dir, exist_ok=True)
        os.makedirs(self.item_dir, exist_ok=True)
        os.makedirs(self.reference_dir, exist_ok=True)

        self.current_character = {
            'character_data': None,
            'reference_image': None,
            'style_preferences': {},
            'generated_sprites': []
        }

    # -------------------------------------------------------
    # Reference image save
    # -------------------------------------------------------
    def save_reference_image(self, uploaded_file):
        if uploaded_file is None:
            return None

        try:
            timestamp = int(time.time())
            filename = f"reference_{timestamp}.png"
            reference_path = os.path.join(self.reference_dir, filename)

            if hasattr(uploaded_file, 'name'):
                shutil.copy2(uploaded_file.name, reference_path)
            else:
                if isinstance(uploaded_file, str):
                    shutil.copy2(uploaded_file, reference_path)
                elif hasattr(uploaded_file, 'save'):
                    uploaded_file.save(reference_path)

            # Validate saved image
            test_image = PIL.Image.open(reference_path)
            try:
                test_image.verify()
            except Exception:
                pass

            print(f"Reference image saved to: {reference_path}")
            return reference_path

        except Exception as e:
            print(f"Error saving reference image: {e}")
            return None

    # -------------------------------------------------------
    # **FIXED** Image Convert + Save
    # -------------------------------------------------------
    def save_image(self, response, path, target_width=None, target_height=None, lock_aspect_ratio=False, use_percentage=False):
        """Save Gemini-generated image with robust type handling."""
        
        for part in response.parts:
            image = part.as_image()
            if image is None:
                continue

            # -------------------------------
            # 1) Google Gemini Image 타입 변환
            # -------------------------------
            if type(image).__name__ == "Image" and "google.genai" in str(type(image)):
                print("🔍 Gemini Image detected — converting...")

                # Case A: image_bytes (권장)
                if hasattr(image, "image_bytes") and image.image_bytes:
                    try:
                        image = Image.open(BytesIO(image.image_bytes))
                    except Exception as e:
                        print(f"❌ image_bytes 변환 실패: {e}")

                # Case B: 내부 _pil_image
                elif hasattr(image, "_pil_image") and image._pil_image:
                    try:
                        image = image._pil_image
                    except Exception as e:
                        print(f"❌ _pil_image 사용 실패: {e}")

                else:
                    attrs = [a for a in dir(image) if not a.startswith("__")]
                    raise ValueError(
                        f"Gemini 이미지 변환 불가. 사용 가능한 속성: {attrs}"
                    )

            # -------------------------------
            # 2) 정상적인 PIL 이미지인지 체크
            # -------------------------------
            if not isinstance(image, Image.Image):
                raise ValueError(f"Unexpected image type: {type(image)}")

            # -------------------------------
            # 3) Resize (기존 코드 유지)
            # -------------------------------
            if target_width and target_height and target_width > 0 and target_height > 0:
                orig_w, orig_h = image.size

                if use_percentage:
                    new_w = int(orig_w * (target_width / 100.0))
                    new_h = int(orig_h * (target_height / 100.0))
                else:
                    new_w = int(target_width)
                    new_h = int(target_height)

                # Aspect ratio 유지
                if lock_aspect_ratio:
                    aspect = orig_w / orig_h
                    if new_w / new_h > aspect:
                        new_w = int(new_h * aspect)
                    else:
                        new_h = int(new_w / aspect)

                image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # -------------------------------
            # 4) Save
            # -------------------------------
            image.save(path)
            print(f"✅ Image saved: {path}")
            return image

        return None

    # -------------------------------------------------------
    # Character Generation
    # -------------------------------------------------------
    def generate_character_image(self, character_description, style_preferences=None, reference_image_paths=None,
                                 target_width=None, target_height=None, lock_aspect_ratio=False, use_percentage=False):

        prompt = self._build_character_prompt(character_description, style_preferences)
        content = [prompt]

        # Handle multiple reference images
        if reference_image_paths:
            if isinstance(reference_image_paths, str):
                # Backward compatibility: single path as string
                reference_image_paths = [reference_image_paths]
            
            for ref_path in reference_image_paths:
                if ref_path and os.path.exists(ref_path):
                    content.append(PIL.Image.open(ref_path))
                    print(f"Using reference image: {ref_path}")

        response = self.image_gen_client.models.generate_content(
            model=self.image_gen_model_name,
            contents=content
        )

        ts = int(time.time())
        out_path = os.path.join(self.character_dir, f"character_{ts}.png")
        img = self.save_image(response, out_path, target_width, target_height, lock_aspect_ratio, use_percentage)

        return out_path, img

    # -------------------------------------------------------
    # Character Sprites
    # -------------------------------------------------------
    def generate_character_sprites(self, character_description, actions, style_preferences=None, reference_image_path=None,
                                   target_width=None, target_height=None, lock_aspect_ratio=False, use_percentage=False):

        results = []

        for action in actions:
            prompt = self._build_sprite_prompt(character_description, action, style_preferences)
            content = [prompt]

            if reference_image_path and os.path.exists(reference_image_path):
                content.append(PIL.Image.open(reference_image_path))

            response = self.image_gen_client.models.generate_content(
                model=self.image_gen_model_name,
                contents=content
            )

            ts = int(time.time())
            out_path = os.path.join(self.character_dir, f"character_{action}_{ts}.png")
            img = self.save_image(response, out_path, target_width, target_height, lock_aspect_ratio, use_percentage)

            results.append({
                "action": action,
                "image_path": out_path,
                "image": img
            })

        return results

    # -------------------------------------------------------
    # Background Generation
    # -------------------------------------------------------
    def generate_background_image(self, background_description, orientation="landscape",
                                  style_preferences=None, target_width=None, target_height=None,
                                  lock_aspect_ratio=False, use_percentage=False):

        prompt = self._build_background_prompt(background_description, orientation, style_preferences)

        response = self.image_gen_client.models.generate_content(
            model=self.image_gen_model_name,
            contents=[prompt]
        )

        ts = int(time.time())
        out_path = os.path.join(self.background_dir, f"background_{orientation}_{ts}.png")
        img = self.save_image(response, out_path, target_width, target_height, lock_aspect_ratio, use_percentage)

        return out_path, img

    # -------------------------------------------------------
    # Item Generation
    # -------------------------------------------------------
    def generate_item_image(self, item_description, style_preferences=None, reference_image_path=None,
                            target_width=None, target_height=None, lock_aspect_ratio=False, use_percentage=False):

        prompt = self._build_item_prompt(item_description, style_preferences)
        content = [prompt]

        if reference_image_path and os.path.exists(reference_image_path):
            content.append(PIL.Image.open(reference_image_path))
            print(f"Using reference image: {reference_image_path}")

        response = self.image_gen_client.models.generate_content(
            model=self.image_gen_model_name,
            contents=content
        )

        ts = int(time.time())
        out_path = os.path.join(self.item_dir, f"item_{ts}.png")
        img = self.save_image(response, out_path, target_width, target_height, lock_aspect_ratio, use_percentage)

        return out_path, img

    # =====================================================
    # Prompt builders (기존 유지)
    # =====================================================
    def _build_character_prompt(self, character_description, style_preferences=None):
        base = f"""
        Create a 2D game character sprite:
        {character_description}

        Requirements:
        - Clear at small sizes
        - Strong silhouette
        - Consistent 2D game art style
        - Follow reference image if provided
        """

        if style_preferences:
            base += "\n" + self._get_style_instructions(style_preferences)
        return base

    def _build_sprite_prompt(self, character_description, action, style_preferences=None):
        base = f"""
        Create a 2D game character sprite performing the action: {action}
        Character: {character_description}

        Requirements:
        - Suitable for sprite animation
        - Clear & consistent style
        - Follow reference image if provided
        """

        if style_preferences:
            base += "\n" + self._get_style_instructions(style_preferences)
        return base

    def _build_background_prompt(self, background_description, orientation, style_preferences=None):
        aspect = "16:9" if orientation == "landscape" else "9:16"
        base = f"""
        Create a 2D game background:
        {background_description}

        Requirements:
        - {orientation} orientation ({aspect})
        - Parallax-ready
        - No characters
        - Consistent 2D art style
        """

        if style_preferences:
            base += "\n" + self._get_style_instructions(style_preferences)
        return base

    def _build_item_prompt(self, item_description, style_preferences=None):
        base = f"""
        Create a 2D game item sprite:
        {item_description}

        Requirements:
        - Clear at small sizes
        - Transparent background
        - Consistent art style
        """

        if style_preferences:
            base += "\n" + self._get_style_instructions(style_preferences)
        return base

    def _get_style_instructions(self, style_preferences):
        instructions = []
        for key in ["art_style", "mood", "color_palette", "character_style", "line_style", "composition", "additional_notes"]:
            if style_preferences.get(key):
                instructions.append(f"{key.replace('_',' ').title()}: {style_preferences[key]}")
        return "\n".join(instructions)


# Global generator instance
_global_generator = None

def get_global_generator():
    global _global_generator
    if _global_generator is None:
        _global_generator = GameAssetGenerator()
    return _global_generator
