"""UI 컴포넌트 생성 함수들"""

import gradio as gr
from .gradio_helpers import DEFAULT_CHOICES, FILE_TYPES
from .utils import ART_STYLES, MOOD_OPTIONS, COLOR_PALETTES, CHARACTER_STYLES, LINE_STYLES, COMPOSITION_STYLES

def create_style_dropdowns():
    """스타일 설정 드롭다운들을 생성하는 공통 함수"""
    return {
        'art_style': gr.Dropdown(choices=DEFAULT_CHOICES + ART_STYLES, value="None", label="Art Style"),
        'mood': gr.Dropdown(choices=DEFAULT_CHOICES + MOOD_OPTIONS, value="None", label="Overall Mood"),
        'color_palette': gr.Dropdown(choices=DEFAULT_CHOICES + COLOR_PALETTES, value="None", label="Color Palette"),
        'character_style': gr.Dropdown(choices=DEFAULT_CHOICES + CHARACTER_STYLES, value="None", label="Character Style"),
        'line_style': gr.Dropdown(choices=DEFAULT_CHOICES + LINE_STYLES, value="None", label="Line Art Style"),
        'composition': gr.Dropdown(choices=DEFAULT_CHOICES + COMPOSITION_STYLES, value="None", label="Composition Style")
    }

def create_config_dropdown(initial_configs, label="Saved Settings Selection"):
    """설정 불러오기 드롭다운을 생성하는 공통 함수"""
    return gr.Dropdown(
        choices=initial_configs,
        value="None",
        label=label,
        interactive=True,
        allow_custom_value=True
    )

def create_reference_upload(
    label="Upload Reference",
    file_types=FILE_TYPES,
    visible=True,
    show_label=True,
    elem_id=None,
    elem_classes=None,
    **kwargs
):
    """참조 이미지 업로드 컴포넌트를 생성하는 공통 함수"""
    return gr.File(
        label=label,
        file_types=file_types,
        visible=visible,
        show_label=show_label,
        elem_id=elem_id,
        elem_classes=elem_classes,
        type="filepath",
        **kwargs
    )

def create_image_size_controls():
    """Create image size adjustment UI components"""
    with gr.Group():
        gr.Markdown("### Image Size Adjustment")
        with gr.Row():
            with gr.Column(scale=1):
                image_width = gr.Number(
                    label="Width",
                    value=512,
                    minimum=64,
                    maximum=4096,
                    step=64,
                    precision=0
                )
            with gr.Column(scale=1):
                image_height = gr.Number(
                    label="Height",
                    value=512,
                    minimum=64,
                    maximum=4096,
                    step=64,
                    precision=0
                )
            with gr.Column(scale=1):
                use_percentage = gr.Checkbox(
                    label="%",
                    value=False,
                    info="Use percentage scaling"
                )
        lock_aspect_ratio = gr.Checkbox(
            label="Lock Aspect Ratio",
            value=False
        )
    return image_width, image_height, lock_aspect_ratio, use_percentage

