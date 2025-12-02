"""설정 관리 함수들"""

import gradio as gr
from .config_manager import get_global_config_manager
from .gradio_helpers import DEFAULT_CHOICES

def save_config_interface(config_name, art_style, mood, color_palette, 
                         character_style, line_style, composition, additional_notes):
    """설정을 저장하는 인터페이스 함수"""
    config_manager = get_global_config_manager()
    try:
        if not config_name.strip():
            return "❌ Please enter a setting name."
        
        # 설정 데이터 구성
        config_data = {
            "art_style": art_style if art_style != "None" else None,
            "mood": mood if mood != "None" else None,
            "color_palette": color_palette if color_palette != "None" else None,
            "character_style": character_style if character_style != "None" else None,
            "line_style": line_style if line_style != "None" else None,
            "composition": composition if composition != "None" else None,
            "additional_notes": additional_notes.strip() if additional_notes.strip() else None
        }
        
        # 빈 값들 제거
        config_data = {k: v for k, v in config_data.items() if v is not None}
        
        if config_manager.save_config(config_name, config_data):
            return f"✅ Setting '{config_name}' saved successfully!"
        else:
            return "❌ Failed to save setting."
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def load_config_interface(config_name):
    """설정을 불러오는 인터페이스 함수"""
    config_manager = get_global_config_manager()
    try:
        if not config_name or config_name == "None":
            return "None", "None", "None", "None", "None", "None", "None", "설정을 선택해주세요."
        
        # config_manager.load_config()는 이미 data 필드를 반환함
        config_data = config_manager.load_config(config_name)
        
        if config_data:
            return (
                config_data.get("art_style", "None"),
                config_data.get("mood", "None"),
                config_data.get("color_palette", "None"),
                config_data.get("character_style", "None"),
                config_data.get("line_style", "None"),
                config_data.get("composition", "None"),
                config_data.get("additional_notes", ""),
                f"✅ 설정 '{config_name}'을 불러왔습니다!"
            )
        else:
            return "None", "None", "None", "None", "None", "None", "None", "❌ Setting not found."
            
    except Exception as e:
        return "None", "None", "None", "None", "None", "None", "None", f"❌ Error: {str(e)}"

def get_saved_configs():
    """저장된 설정 목록을 반환"""
    config_manager = get_global_config_manager()
    configs = config_manager.get_config_names()
    return DEFAULT_CHOICES + configs

def delete_config_interface(config_name):
    """설정을 삭제하는 인터페이스 함수"""
    from .gradio_helpers import _dropdown_update
    config_manager = get_global_config_manager()
    try:
        if not config_name or config_name == "None":
            configs = get_saved_configs()
            return "Please select a setting to delete.", _dropdown_update(configs)

        if config_manager.delete_config(config_name):
            configs = get_saved_configs()
            return f"✅ Setting '{config_name}' deleted successfully!", _dropdown_update(configs)
        else:
            configs = get_saved_configs()
            return f"❌ Failed to delete setting '{config_name}'.", _dropdown_update(configs)

    except Exception as e:
        configs = get_saved_configs()
        return f"❌ Error: {str(e)}", _dropdown_update(configs)
