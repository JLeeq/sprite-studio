"""이벤트 핸들러 설정"""

from .gradio_prompt_previews import preview_character_prompt, preview_sprite_prompt, preview_background_prompt, preview_item_prompt
from .gradio_generation_interfaces import generate_character_interface, generate_character_sprites_interface, generate_background_interface, generate_item_interface
from .gradio_config_management import save_config_interface, load_config_interface, delete_config_interface, get_saved_configs
from .gradio_helpers import _refresh_all_config_dropdowns

def _setup_event_handlers(
    # 생성 버튼들
    generate_character_btn, generate_sprites_btn, generate_background_btn, generate_item_btn,
    # 입력 컴포넌트들
    character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes, reference_image, character_item_image,
    sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes, sprite_reference_image,
    background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes,
    item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes, item_reference_image,
    # 출력 컴포넌트들
    character_output, character_status, sprites_gallery, sprites_status, background_output, background_status, item_output, item_status,
    # 프롬프트 미리보기 컴포넌트들
    character_prompt_display, sprites_prompt_display, background_prompt_display, item_prompt_display,
    # 설정 관리 컴포넌트들
    save_config_btn, load_config_btn, delete_config_btn, save_config_name, save_art_style, save_mood, save_color_palette, save_character_style, save_line_style, save_composition, save_additional_notes, save_status, load_status, delete_status,
    # 설정 드롭다운들
    load_config_dropdown, delete_config_dropdown, char_config_dropdown, sprite_config_dropdown, bg_config_dropdown, item_config_dropdown,
    # 설정 불러오기 버튼들
    char_load_config_btn, sprite_load_config_btn, bg_load_config_btn, item_load_config_btn,
    # 이미지 크기 조정 컴포넌트들
    char_image_width=None, char_image_height=None, char_lock_aspect_ratio=None, char_use_percentage=None,
    sprite_image_width=None, sprite_image_height=None, sprite_lock_aspect_ratio=None, sprite_use_percentage=None,
    bg_image_width=None, bg_image_height=None, bg_lock_aspect_ratio=None, bg_use_percentage=None,
    item_image_width=None, item_image_height=None, item_lock_aspect_ratio=None, item_use_percentage=None
):
    """모든 이벤트 핸들러를 설정하는 함수"""
    
    # 프롬프트 미리보기 이벤트 핸들러
    character_description.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    art_style.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    mood.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    color_palette.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    character_style.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    line_style.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    composition.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    additional_notes.change(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )
    
    # 스프라이트 프롬프트 미리보기 이벤트 핸들러
    sprite_character_description.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    actions_text.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_art_style.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_mood.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_color_palette.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_character_style.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_line_style.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_composition.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )
    
    sprite_additional_notes.change(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )

    # Sprites 생성 래퍼 함수는 create_game_asset_interface 내부에서 정의됨
    
    # 배경 프롬프트 미리보기 이벤트 핸들러
    background_description.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    orientation.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    bg_art_style.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    bg_mood.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    bg_color_palette.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    bg_line_style.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    bg_composition.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )
    
    bg_additional_notes.change(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )

    # 아이템 프롬프트 미리보기 이벤트 핸들러
    item_description.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )
    
    item_art_style.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )
    
    item_mood.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )
    
    item_color_palette.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )
    
    item_line_style.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )
    
    item_composition.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )
    
    item_additional_notes.change(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, 
        item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )

    # Item 생성 래퍼 함수는 create_game_asset_interface 내부에서 정의됨
    

    # 1) 저장: 실제 저장 -> 모든 드롭다운 갱신
    save_config_btn.click(
        fn=save_config_interface,
        inputs=[save_config_name, save_art_style, save_mood, save_color_palette,
                save_character_style, save_line_style, save_composition, save_additional_notes],
        outputs=[save_status],
    ).then(
        fn=_refresh_all_config_dropdowns,
        outputs=[load_config_dropdown, delete_config_dropdown, char_config_dropdown,
                 sprite_config_dropdown, bg_config_dropdown, item_config_dropdown],
    )

    # 2) 불러오기(Setting 탭): 선택한 설정을 오른쪽 저장 필드들에 채움
    load_config_btn.click(
        fn=load_config_interface,
        inputs=[load_config_dropdown],
        outputs=[save_art_style, save_mood, save_color_palette, save_character_style,
                 save_line_style, save_composition, save_additional_notes, load_status],
    )

    # 3) 삭제: 실제 삭제 -> 모든 드롭다운 갱신
    delete_config_btn.click(
        fn=delete_config_interface,
        inputs=[delete_config_dropdown],
        outputs=[delete_status, delete_config_dropdown],  # 즉시 자신 드롭다운 반영
    ).then(
        fn=_refresh_all_config_dropdowns,
        outputs=[load_config_dropdown, delete_config_dropdown, char_config_dropdown,
                 sprite_config_dropdown, bg_config_dropdown, item_config_dropdown],
    )

    # -------------------------
    # 탭별 불러오기 버튼 (유지)
    # -------------------------
    char_load_config_btn.click(
        fn=load_config_interface,
        inputs=[char_config_dropdown],
        outputs=[art_style, mood, color_palette, character_style, line_style, composition,
                 additional_notes, character_status],
    ).then(
        fn=preview_character_prompt,
        inputs=[character_description, art_style, mood, color_palette, character_style, line_style, composition, additional_notes],
        outputs=[character_prompt_display]
    )

    sprite_load_config_btn.click(
        fn=load_config_interface,
        inputs=[sprite_config_dropdown],
        outputs=[sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style,
                 sprite_line_style, sprite_composition, sprite_additional_notes, sprites_status],
    ).then(
        fn=preview_sprite_prompt,
        inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes],
        outputs=[sprites_prompt_display]
    )

    bg_load_config_btn.click(
        fn=load_config_interface,
        inputs=[bg_config_dropdown],
        outputs=[bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition,
                 bg_additional_notes, background_status],
    ).then(
        fn=preview_background_prompt,
        inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes],
        outputs=[background_prompt_display]
    )

    item_load_config_btn.click(
        fn=load_config_interface,
        inputs=[item_config_dropdown],
        outputs=[item_art_style, item_mood, item_color_palette, item_line_style,
                 item_composition, item_additional_notes, item_status],
    ).then(
        fn=preview_item_prompt,
        inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes],
        outputs=[item_prompt_display]
    )



