"""프롬프트 미리보기 함수들"""

from .game_asset_generator import get_global_generator
from .gradio_helpers import build_user_preferences

def preview_character_prompt(character_description, art_style, mood, color_palette, 
                           character_style, line_style, composition, additional_notes):
    """Preview the generated prompt for character generation."""
    if not character_description or not character_description.strip():
        return "Enter a character description to see the generated prompt..."
    
    try:
        generator = get_global_generator()
        user_preferences = build_user_preferences(art_style, mood, color_palette, character_style, line_style, composition, additional_notes)
        prompt = generator._build_character_prompt(character_description, user_preferences)
        return prompt
    except Exception as e:
        return f"Error generating prompt preview: {str(e)}"

def preview_sprite_prompt(character_description, actions_text, art_style, mood, color_palette, 
                         character_style, line_style, composition, additional_notes):
    """Preview the generated prompt for sprite generation."""
    if not character_description or not character_description.strip():
        return "Enter a character description to see the generated prompt..."
    
    if not actions_text or not actions_text.strip():
        return "Enter actions to see the generated prompt..."
    
    try:
        generator = get_global_generator()
        user_preferences = build_user_preferences(art_style, mood, color_palette, character_style, line_style, composition, additional_notes)
        actions = [action.strip() for action in actions_text.split(',') if action.strip()]
        if actions:
            # Show prompt for the first action as an example
            prompt = generator._build_sprite_prompt(character_description, actions[0], user_preferences)
            return prompt
        else:
            return "Enter valid actions separated by commas..."
    except Exception as e:
        return f"Error generating prompt preview: {str(e)}"

def preview_background_prompt(background_description, orientation, art_style, mood, color_palette, 
                            line_style, composition, additional_notes):
    """Preview the generated prompt for background generation."""
    if not background_description or not background_description.strip():
        return "Enter a background description to see the generated prompt..."
    
    try:
        generator = get_global_generator()
        user_preferences = build_user_preferences(art_style, mood, color_palette, None, line_style, composition, additional_notes)
        prompt = generator._build_background_prompt(background_description, orientation, user_preferences)
        return prompt
    except Exception as e:
        return f"Error generating prompt preview: {str(e)}"

def preview_item_prompt(item_description, art_style, mood, color_palette, 
                       line_style, composition, additional_notes):
    """Preview the generated prompt for item generation."""
    if not item_description or not item_description.strip():
        return "Enter an item description to see the generated prompt..."
    
    try:
        generator = get_global_generator()
        user_preferences = build_user_preferences(art_style, mood, color_palette, None, line_style, composition, additional_notes)
        prompt = generator._build_item_prompt(item_description, user_preferences)
        return prompt
    except Exception as e:
        return f"Error generating prompt preview: {str(e)}"
