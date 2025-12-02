"""생성 인터페이스 함수들"""

from .game_asset_generator import get_global_generator
from .gradio_helpers import build_user_preferences

def generate_character_interface(character_description, art_style, mood, color_palette, 
                               character_style, line_style, composition, additional_notes, 
                               character_reference_image=None, item_reference_image=None, image_width=None, image_height=None, 
                               lock_aspect_ratio=False, use_percentage=False):
    """Interface function for character generation."""
    generator = get_global_generator()
    try:
        # Build user preferences dictionary
        user_preferences = build_user_preferences(art_style, mood, color_palette, character_style, line_style, composition, additional_notes)
        
        # Handle reference images
        reference_paths = []
        if character_reference_image is not None:
            char_path = generator.save_reference_image(character_reference_image)
            if char_path:
                reference_paths.append(char_path)
        
        if item_reference_image is not None:
            item_path = generator.save_reference_image(item_reference_image)
            if item_path:
                reference_paths.append(item_path)
        
        # Generate character image with multiple references
        image_path, saved_image = generator.generate_character_image(
            character_description, user_preferences, reference_paths,
            image_width, image_height, lock_aspect_ratio, use_percentage
        )
        
        return image_path, "✅ Character generated successfully!"
        
    except Exception as e:
        error_msg = f"❌ Error generating character: {str(e)}"
        return None, error_msg

def generate_character_sprites_interface(character_description, actions_text, art_style, mood, 
                                       color_palette, character_style, line_style, composition, 
                                       additional_notes, reference_image, image_width=None, 
                                       image_height=None, lock_aspect_ratio=False, use_percentage=False):
    """Interface function for character sprite generation."""
    generator = get_global_generator()
    try:
        # Parse actions from text input
        actions = [action.strip() for action in actions_text.split(',') if action.strip()]
        if not actions:
            return [], "Please provide at least one action separated by commas."
        
        # Build user preferences dictionary
        user_preferences = build_user_preferences(art_style, mood, color_palette, character_style, line_style, composition, additional_notes)
        
        # Handle reference image
        reference_path = None
        if reference_image is not None:
            reference_path = generator.save_reference_image(reference_image)
        
        # Generate character sprites
        generated_sprites = generator.generate_character_sprites(
            character_description, actions, user_preferences, reference_path,
            image_width, image_height, lock_aspect_ratio, use_percentage
        )
        
        # Return image paths for gallery display
        image_paths = [sprite['image_path'] for sprite in generated_sprites]
        
        return image_paths, f"✅ Generated {len(generated_sprites)} sprites successfully!"
        
    except Exception as e:
        error_msg = f"❌ Error generating sprites: {str(e)}"
        return [], error_msg

def generate_background_interface(background_description, orientation, art_style, mood, 
                                color_palette, line_style, composition, additional_notes,
                                image_width=None, image_height=None, lock_aspect_ratio=False, 
                                use_percentage=False):
    """Interface function for background generation."""
    generator = get_global_generator()
    try:
        # Build user preferences dictionary
        user_preferences = build_user_preferences(art_style, mood, color_palette, None, line_style, composition, additional_notes)
        
        # Generate background image
        image_path, saved_image = generator.generate_background_image(
            background_description, orientation, user_preferences,
            image_width, image_height, lock_aspect_ratio, use_percentage
        )
        
        return image_path, f"✅ Background generated successfully! ({orientation})"
        
    except Exception as e:
        error_msg = f"❌ Error generating background: {str(e)}"
        return None, error_msg

def generate_item_interface(item_description, art_style, mood, color_palette, 
                          line_style, composition, additional_notes, reference_image,
                          image_width=None, image_height=None, lock_aspect_ratio=False, 
                          use_percentage=False):
    """Interface function for item generation."""
    generator = get_global_generator()
    try:
        # Build user preferences dictionary
        user_preferences = build_user_preferences(art_style, mood, color_palette, None, line_style, composition, additional_notes)
        
        # Handle reference image
        reference_path = None
        if reference_image is not None:
            reference_path = generator.save_reference_image(reference_image)
        
        # Generate item image
        image_path, saved_image = generator.generate_item_image(
            item_description, user_preferences, reference_path,
            image_width, image_height, lock_aspect_ratio, use_percentage
        )
        
        return image_path, "✅ Item generated successfully!"
        
    except Exception as e:
        error_msg = f"❌ Error generating item: {str(e)}"
        return None, error_msg
