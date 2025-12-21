"""
픽셀 캐릭터 생성기 - Gemini API를 사용한 픽셀 아트 캐릭터 생성
"""

import os
import PIL
from google import genai
from dotenv import load_dotenv
import time
from PIL import Image
import json
from pathlib import Path
import base64
import io

# Load environment variables
load_dotenv()


class PixelCharacterGenerator:
    def __init__(self):
        """Initialize the character generator with API client and configuration."""
        # Get API key from environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            print("⚠️  GEMINI_API_KEY not found in environment variables.")
            print("Please set your API key in .env file: GEMINI_API_KEY=your_key_here")
            raise ValueError("GEMINI_API_KEY is required but not found.")
        
        # API key loaded (not logging to prevent leaks)
        
        self.output_dir = os.getenv("OUTPUT_DIR", "data/output")
        self.image_gen_model_name = os.getenv("IMAGE_MODEL_NAME", "gemini-2.5-flash-image-preview")
        
        # Initialize Gemini client
        try:
            print("🔄 Initializing Gemini client...")
            self.image_gen_client = genai.Client(api_key=self.api_key)
            print("✅ Gemini client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini client: {e}")
            raise ValueError(f"Failed to initialize Gemini API client: {e}")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def save_image(self, response, path):
        """Save the generated image from response."""
        for part in response.parts:
            if image := part.as_image():
                image.save(path)
                return image
        return None

# Global generator instance
_global_generator = None

def get_global_pixel_generator():
    """Get or create the global pixel generator instance."""
    global _global_generator
    if _global_generator is None:
        _global_generator = PixelCharacterGenerator()
    return _global_generator

def generate_pixel_character_interface(description: str, character_reference_image=None, item_reference_image=None):
    """Interface function for pixel character generation - transparent PNG, front view, original quality."""
    generator = get_global_pixel_generator()
    try:
        if not description or not description.strip():
            return "❌ Please enter a character description.", None
        
        # Build detailed prompt for PIXEL ART character generation
        prompt = "Create a PIXEL ART character sprite with these specifications:\n\n"
        prompt += f"Character: {description}\n"
        
        # Add reference image instructions
        if item_reference_image:
            prompt += "\nThe character should be holding or using the item shown in the reference image.\n"
        
        prompt += "\nMANDATORY PIXEL ART STYLE REQUIREMENTS:\n"
        prompt += "- **CONSISTENT STYLE**: Must look like it came from the same game/site as other characters\n"
        prompt += "- **PIXEL ART ONLY**: Retro pixel art style, NOT smooth/realistic art\n"
        prompt += "- **CHIBI PROPORTIONS**: Large head, small body - cute deformed style\n"
        prompt += "- **HEAD TO BODY RATIO: 1:1** - Head size MUST equal body size (equal proportions)\n"
        prompt += "- Clear pixelated edges, visible individual pixels\n"
        prompt += "- Limited color palette (8-16 colors recommended)\n"
        prompt += "- Clean pixel-perfect outlines\n"
        prompt += "- Front-facing view\n"
        prompt += "- Single character, centered composition\n"
        prompt += "- White background (will be made transparent)\n"
        prompt += "- Game sprite aesthetic (like 8-bit, 16-bit, or 32-bit era)\n"
        prompt += "- Sharp, blocky pixel style - NOT anti-aliased or smooth\n"
        prompt += "- Retro video game character design\n"
        prompt += "- IMPORTANT: Face/head height = body height (1:1 ratio)\n"
        prompt += "- **UNIFORM STYLE**: Same art style, proportions, and rendering as reference characters\n"
        
        # Generate timestamp for unique filename
        timestamp = int(time.time())
        temp_output_path = os.path.join(generator.output_dir, f"character_temp_{timestamp}.png")
        output_path = os.path.join(generator.output_dir, f"character_{timestamp}.png")
        
        # Prepare content list with prompt and reference images
        contents = [prompt]
        
        # Add character reference image if provided
        if character_reference_image:
            try:
                if hasattr(character_reference_image, 'name'):
                    ref_path = character_reference_image.name
                else:
                    ref_path = character_reference_image
                
                if ref_path and os.path.exists(ref_path):
                    ref_img = Image.open(ref_path)
                    contents.append(ref_img)
                    print(f"Using character reference image: {ref_path}")
            except Exception as e:
                print(f"Warning: Could not load character reference image: {e}")
        
        # Add item reference image if provided
        if item_reference_image:
            try:
                if hasattr(item_reference_image, 'name'):
                    item_path = item_reference_image.name
                else:
                    item_path = item_reference_image
                
                if item_path and os.path.exists(item_path):
                    item_img = Image.open(item_path)
                    contents.append(item_img)
                    print(f"Using item reference image: {item_path}")
            except Exception as e:
                print(f"Warning: Could not load item reference image: {e}")
        
        # Generate image using Gemini
        print(f"🎮 Generating PIXEL ART character: {description[:50]}...")
        print(f"   Style: Pixel Art (Retro Game Sprite)")
        if character_reference_image:
            print(f"   Character reference: Yes")
        if item_reference_image:
            print(f"   Item reference: Yes")
        
        try:
            response = generator.image_gen_client.models.generate_content(
                model=generator.image_gen_model_name,
                contents=contents
            )
            
            # Save the generated image
            saved_image = generator.save_image(response, temp_output_path)
            
            if saved_image:
                # Use original high-quality image without resizing
                img = Image.open(temp_output_path)
                
                # Convert to RGBA if not already (for transparency support)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Save as high-quality PNG
                img.save(output_path, 'PNG', optimize=False, quality=100)
                
                # Clean up temp file
                if os.path.exists(temp_output_path) and temp_output_path != output_path:
                    os.remove(temp_output_path)
                
                actual_size = img.size
                print(f"✅ PIXEL ART character generated successfully: {output_path} ({actual_size[0]}x{actual_size[1]})")
                return f"✅ Pixel art character generated successfully! 🎮 (Size: {actual_size[0]}x{actual_size[1]} PNG)", output_path
            else:
                return "❌ Image generation failed. Please try again.", None
                
        except Exception as gen_error:
            print(f"Generation error: {gen_error}")
            return f"❌ Generation error: {str(gen_error)}", None
            
    except Exception as e:
        import traceback
        print(f"Error in generate_character_interface: {e}")
        print(traceback.format_exc())
        return f"❌ Error occurred: {str(e)}", None

