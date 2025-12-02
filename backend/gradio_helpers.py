"""공통 헬퍼 함수들"""
from typing import Dict
import gradio as gr
from .config_manager import get_global_config_manager

DEFAULT_CHOICES = ["None"]
FILE_TYPES = [".png", ".jpg", ".jpeg", ".webp"]


def _default_user_session() -> Dict[str, str | bool | int | None]:
    return {
        "authenticated": False,
        "user_id": None,
        "email": None,
        "access_token": None,
        "tokens": 0,
        "last_image_url": None,
    }


def _format_token_text(tokens: int) -> str:
    return f"🎟️ Tokens Remaining: **{tokens}**"


def _unauthorized_response(message: str, last_image_url: str | None):
    token_text = "Please sign in to generate assets."
    last_image_update = (
        gr.update(value=last_image_url, visible=True)
        if last_image_url
        else gr.update(value=None, visible=False)
    )
    return token_text, last_image_update


def _dropdown_update(choices, value="None"):
    """공통으로 사용하는 드롭다운 업데이트 헬퍼"""
    return gr.update(choices=choices, value=value)


def _refresh_all_config_dropdowns():
    """저장된 설정을 다시 읽어 모든 드롭다운을 갱신"""
    from .gradio_config_management import get_saved_configs
    configs = get_saved_configs()
    update = _dropdown_update(configs)
    return (update, update, update, update, update, update)


def build_user_preferences(art_style, mood, color_palette, character_style, line_style, composition, additional_notes):
    """사용자 설정을 딕셔너리로 구성하는 공통 함수"""
    user_preferences = {}
    if art_style and art_style != "None":
        user_preferences['art_style'] = art_style
    if mood and mood != "None":
        user_preferences['mood'] = mood
    if color_palette and color_palette != "None":
        user_preferences['color_palette'] = color_palette
    if character_style and character_style != "None":
        user_preferences['character_style'] = character_style
    if line_style and line_style != "None":
        user_preferences['line_style'] = line_style
    if composition and composition != "None":
        user_preferences['composition'] = composition
    if additional_notes and additional_notes.strip():
        user_preferences['additional_notes'] = additional_notes.strip()
    return user_preferences



