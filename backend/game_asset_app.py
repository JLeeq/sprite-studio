import gradio as gr
import os
import time
from typing import Dict

import numpy as np
from PIL import Image

import zipfile
import shutil

from .game_asset_generator import get_global_generator
from .utils import ART_STYLES, MOOD_OPTIONS, COLOR_PALETTES, CHARACTER_STYLES, LINE_STYLES, COMPOSITION_STYLES
from .config_manager import get_global_config_manager
from .pixel_character_generator import generate_pixel_character_interface
from .supabase_client import (
    sign_up_user,
    sign_in_user,
    sign_out_user,
    ensure_user_token_balance,
    get_user_token_balance,
    consume_user_token,
    record_generated_image,
    get_last_generated_image_url,
    validate_access_token,
)

# 분리된 모듈들 import
from .gradio_helpers import (
    _default_user_session,
    _format_token_text,
    _unauthorized_response,
    _dropdown_update,
    _refresh_all_config_dropdowns,
    build_user_preferences,
    DEFAULT_CHOICES,
    FILE_TYPES,
)
from .gradio_prompt_previews import (
    preview_character_prompt,
    preview_sprite_prompt,
    preview_background_prompt,
    preview_item_prompt,
)
from .gradio_generation_interfaces import (
    generate_character_interface,
    generate_character_sprites_interface,
    generate_background_interface,
    generate_item_interface,
)
from .gradio_animation import (
    create_sprite_animation_zip,
    generate_pixel_character,
    generate_sprite_animation,
    generate_dead_animation,
    generate_universal_animation,
    update_animation_info,
)
from .gradio_config_management import (
    save_config_interface,
    load_config_interface,
    delete_config_interface,
    get_saved_configs,
)
from .gradio_ui_components import (
    create_style_dropdowns,
    create_config_dropdown,
    create_reference_upload,
    create_image_size_controls,
)
from .gradio_event_handlers import _setup_event_handlers
from .gradio_styles import ENHANCED_STYLE_CSS

def create_game_asset_interface():
    # 앱 시작 시 저장된 설정 목록을 가져옴
    initial_configs = get_saved_configs()
    default_animation_text, default_frame_text = update_animation_info("attack")
    
    # Enhanced 스타일 CSS
    ENHANCED_STYLE_CSS = """
    /* Enhanced 스타일 디자인 */
    :root {
        --enhanced-bg: #ffffff;
        --enhanced-text: #1a1a1a;
        --enhanced-accent: #4285f4;
        --enhanced-border: #dadce0;
        --enhanced-hover: #f8f9fa;
        --enhanced-shadow: 0 1px 6px rgba(32,33,36,.28);
        --enhanced-shadow-hover: 0 2px 8px rgba(32,33,36,.3);
    }
    
    /* 모든 탭에 Enhanced 스타일 적용 (Settings 제외) */
    .tab-nav {
        border-bottom: 2px solid var(--enhanced-border);
    }
    
    .tab-nav button {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Press Start 2P', 'Share Tech Mono', 'VT323', 'Google Sans', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        transition: all 0.2s;
    }

    .gradio-tabs button[role="tab"],
    .gradio-tabs button[aria-selected="true"],
    .gradio-tabs button[role="tab"] span,
    .gradio-tabs button[aria-selected="true"] span {
        font-family: 'Press Start 2P', 'Share Tech Mono', 'VT323', 'Google Sans', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.85rem;
    }
    
    .tab-nav button:hover {
        background: var(--enhanced-hover);
    }

    .app-title {
        font-family: 'Press Start 2P', 'Share Tech Mono', 'VT323', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        letter-spacing: 0.12em;
        color: var(--enhanced-text);
        margin: 0.5rem 0 0.25rem;
    }

    .app-subtitle {
        font-family: 'Press Start 2P', 'Share Tech Mono', 'VT323', sans-serif;
        font-size: 1rem;
        text-align: center;
        letter-spacing: 0.08em;
        color: var(--enhanced-accent);
        margin-bottom: 1rem;
    }
    
    /* 탭 컨텐츠 영역 */
    .enhanced-tab-content {
        min-height: 70vh;
        position: relative;
        background: var(--enhanced-bg);
        padding: 2rem;
    }
    
    /* Settings 탭은 제외 */
    #settings-tab,
    #settings-tab .enhanced-tab-content {
        background: transparent;
    }
    
    /* Character Creation 탭 전용 스타일 */
    #character-creation-tab {
        min-height: 80vh;
        position: relative;
        background: var(--enhanced-bg);
        overflow-y: auto;
        padding-bottom: 220px;
    }
    
    /* 중앙 컨테이너 */
    .enhanced-center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 50vh;
        padding: 2rem;
        position: relative;
    }
    
    /* Welcome 텍스트 스타일 */
    .enhanced-welcome-text {
        font-size: 2.2rem;
        font-weight: 400;
        color: var(--enhanced-text);
        margin-bottom: 3rem;
        text-align: center;
        opacity: 1;
        transition: opacity 0.3s ease, height 0.3s ease;
        font-family: 'Press Start 2P', 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        letter-spacing: 1px;
    }
    
    .enhanced-welcome-text.hidden {
        opacity: 0;
        height: 0;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    
    /* 생성된 이미지 컨테이너 */
    .enhanced-image-container {
        max-width: 600px;
        width: 100%;
        margin: 2rem auto;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(20px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    /* 검색창 컨테이너 (하단 고정) */
    .enhanced-search-container {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 600px;
        z-index: 1000;
        background: transparent;
    }
    
    /* Character Creation 탭에 패딩 추가 (하단 검색창 공간 확보) */
    #character-creation-tab .enhanced-center-container {
        padding-bottom: 120px;
    }
    
    /* 모든 탭의 그룹 스타일 개선 */
    .gr-group {
        background: white;
        border: 1px solid var(--enhanced-border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--enhanced-shadow);
        transition: box-shadow 0.2s;
    }
    
    .gr-group:hover {
        box-shadow: var(--enhanced-shadow-hover);
    }
    
    /* 버튼 스타일 개선 */
    button.primary,
    button[variant="primary"] {
        background: linear-gradient(135deg, var(--enhanced-accent), #6366f1);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        box-shadow: var(--enhanced-shadow-md);
        transition: all 0.2s;
    }
    
    button.primary:hover,
    button[variant="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--enhanced-shadow-hover);
    }
    
    /* 입력 필드 스타일 */
    input, textarea, select {
        border-radius: 8px;
        border: 1px solid var(--enhanced-border);
        padding: 0.75rem;
        transition: all 0.2s;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: var(--enhanced-accent);
        box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
        outline: none;
    }
    
    /* 이미지 출력 스타일 */
    .generated-image,
    img {
        border-radius: 12px;
        box-shadow: var(--enhanced-shadow-lg);
    }
    
    .enhanced-search-box {
        display: flex;
        align-items: center;
        background: white;
        border: 1px solid var(--enhanced-border);
        border-radius: 24px;
        padding: 0.75rem 1rem;
        box-shadow: var(--enhanced-shadow);
        transition: box-shadow 0.2s, border-color 0.2s;
    }
    
    .enhanced-search-box:focus-within {
        box-shadow: var(--enhanced-shadow-hover);
        border-color: var(--enhanced-accent);
    }
    
    .enhanced-search-input {
        flex: 1;
        border: none;
        outline: none;
        font-size: 1rem;
        padding: 0.5rem;
        background: transparent;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .enhanced-search-input::placeholder {
        color: #9aa0a6;
    }
    
    /* + 버튼 스타일 (원 모양) */
    .enhanced-upload-btn {
        width: 40px;
        height: 40px;
        min-width: 40px;
        min-height: 40px;
        border-radius: 50%;
        border: 1px solid var(--enhanced-border);
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin-right: 0.5rem;
        transition: all 0.2s;
        font-size: 1.5rem;
        color: var(--enhanced-accent);
        font-weight: 300;
        padding: 0;
        flex-shrink: 0;
    }
    
    .enhanced-upload-btn:hover {
        background: var(--enhanced-hover);
        border-color: var(--enhanced-accent);
        transform: scale(1.05);
    }
    
    /* 숨겨진 파일 업로드 */
    .enhanced-hidden-upload {
        display: none !important;
    }
    
    /* 모드 선택 버튼 (상단 우측) */
    .enhanced-mode-selector {
        position: absolute;
        top: 1rem;
        right: 1rem;
        z-index: 100;
    }
    
    /* 고급 설정 (Accordion) */
    .enhanced-advanced-settings {
        position: absolute;
        top: 1rem;
        left: 1rem;
        right: 1rem;
        bottom: 1rem;
        z-index: 100;
        max-width: 420px;
        max-height: calc(100vh - 2rem);
    }
    
    /* Character 탭에서 Pixel Mode를 Advanced Settings 위로 */
    #character-creation-tab .enhanced-pixel-mode-toggle {
        margin-top: 0;
    }

    #character-creation-tab .enhanced-advanced-settings {
        position: static;
        max-width: none;
        width: 100%;
        margin-bottom: 1.5rem;
    }

    /* Ensure accordion content can scroll independently */
    .enhanced-advanced-settings details,
    .enhanced-advanced-settings .gr-accordion,
    .enhanced-advanced-settings .gr-panel {
        max-height: inherit;
        display: flex;
        flex-direction: column;
    }

    .enhanced-advanced-settings details[open] > div,
    .enhanced-advanced-settings .gr-accordion .gr-panel,
    .enhanced-advanced-settings .gr-accordion-content {
        max-height: calc(100vh - 8rem);
        overflow-y: auto;
        padding-right: 0.5rem;
        padding-bottom: 6rem;
    }

    /* Non-character tabs keep Advanced Settings inline for easier scrolling */
    #item-generation-tab .enhanced-advanced-settings,
    #character-sprites-tab .enhanced-advanced-settings,
    #sprite-animation-tab .enhanced-advanced-settings,
    #background-tab .enhanced-advanced-settings {
        position: static;
        max-width: none;
        width: 100%;
        margin-bottom: 1.5rem;
    }

    #item-generation-tab .enhanced-advanced-settings .gr-accordion-content,
    #character-sprites-tab .enhanced-advanced-settings .gr-accordion-content,
    #sprite-animation-tab .enhanced-advanced-settings .gr-accordion-content,
    #background-tab .enhanced-advanced-settings .gr-accordion-content {
        max-height: none;
        padding-right: 0;
        padding-bottom: 1rem;
    }

    .enhanced-advanced-settings details[open] > div::-webkit-scrollbar,
    .enhanced-advanced-settings .gr-accordion-content::-webkit-scrollbar {
        width: 6px;
    }

    .enhanced-advanced-settings details[open] > div::-webkit-scrollbar-thumb,
    .enhanced-advanced-settings .gr-accordion-content::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 999px;
    }
    
    /* 모달 오버레이 */
    .enhanced-modal-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        backdrop-filter: blur(4px);
    }
    
    .enhanced-modal-overlay.active {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 모달 컨테이너 (Gradio Column을 모달처럼 스타일링) - 오밀조밀하고 예쁘게 */
    .enhanced-modal-container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 20px;
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.25);
        max-width: 700px;
        width: 85%;
        max-height: 85vh;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid var(--enhanced-border);
    }
    
    /* 모달 오버레이 (모달이 열릴 때 배경) */
    .enhanced-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        backdrop-filter: blur(4px);
        display: none;
    }
    
    .enhanced-modal-overlay.active {
        display: block;
    }
    
    /* 모달 헤더 - 오밀조밀하게 */
    .enhanced-modal-header {
        padding: 1rem 1.25rem;
        border-bottom: 1px solid var(--enhanced-border);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    .enhanced-modal-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--enhanced-text);
        margin: 0;
    }
    
    .enhanced-modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--enhanced-text);
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.2s;
    }
    
    .enhanced-modal-close:hover {
        background: var(--enhanced-hover);
    }
    
    /* 모달 바디 (스크롤 가능) - 오밀조밀하게 */
    .enhanced-modal-body {
        padding: 1rem 1.25rem;
        overflow-y: auto;
        overflow-x: hidden;
        flex: 1;
        min-height: 0;
        max-height: calc(85vh - 100px);
    }
    
    /* 모달 내부 섹션 간격 조정 - 오밀조밀하게 */
    .enhanced-modal-body .gr-markdown {
        margin: 0.5rem 0 0.375rem 0;
        font-size: 0.9rem;
    }
    
    .enhanced-modal-body .gr-markdown.small-text {
        font-size: 0.75rem;
        color: #666;
        margin: 0.25rem 0 0.5rem 0;
    }
    
    .enhanced-modal-body .gr-group {
        margin-bottom: 0.75rem;
        padding: 0.875rem;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background: #fafafa;
    }
    
    .enhanced-modal-body .gr-row {
        margin-bottom: 0.5rem;
    }
    
    .enhanced-modal-body .gr-column {
        padding: 0 0.375rem;
    }
    
    .enhanced-modal-body input,
    .enhanced-modal-body select,
    .enhanced-modal-body textarea {
        padding: 0.5rem;
        font-size: 0.875rem;
    }
    
    .enhanced-modal-body label {
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    /* 모달 바디 스크롤바 스타일 */
    .enhanced-modal-body::-webkit-scrollbar {
        width: 8px;
    }
    
    .enhanced-modal-body::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    .enhanced-modal-body::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    .enhanced-modal-body::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* 모달 푸터 - 오밀조밀하게 */
    .enhanced-modal-footer {
        padding: 0.75rem 1.25rem;
        border-top: 1px solid var(--enhanced-border);
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        flex-shrink: 0;
        background: #fafafa;
    }
    
    /* Generate Character 버튼 스타일 */
    .enhanced-generate-btn {
        background: linear-gradient(135deg, var(--enhanced-accent), #6366f1);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.625rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.3);
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .enhanced-generate-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.4);
    }
    
    /* Pixel Mode 체크박스 스타일 (상단 우측) */
    .enhanced-pixel-mode-toggle {
        position: static;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 0.5rem;
        background: white;
        border: 1px solid var(--enhanced-border);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        box-shadow: var(--enhanced-shadow);
        white-space: nowrap;
        width: auto;
        min-width: auto;
        margin: 0 0 0.75rem auto;
    }
    
    .enhanced-pixel-mode-toggle input[type="checkbox"] {
        width: 18px;
        height: 18px;
        cursor: pointer;
    }
    
    .enhanced-pixel-mode-toggle label {
        font-size: 0.875rem;
        cursor: pointer;
        user-select: none;
    }
    
    #hidden-item-upload {
        display: none !important;
    }

    .reference-plus-upload {
        width: 48px;
    }

    .reference-plus-upload [data-testid="file"] {
        padding: 0;
        border: none;
        background: transparent;
    }

    .reference-plus-upload [data-testid="file"] > div:first-child {
        width: 48px;
    }

    .reference-plus-upload [data-testid="file"] label {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 999px;
        border: 1px dashed var(--enhanced-border);
        background: white;
        color: var(--enhanced-accent);
        font-size: 24px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .reference-plus-upload [data-testid="file"] label:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
    }

    .reference-plus-upload [data-testid="file"] label::after {
        content: "+";
    }

    .reference-plus-upload [data-testid="file"] label span,
    .reference-plus-upload [data-testid="file"] label svg {
        display: none !important;
    }
    
    #item-style-upload-btn {
        width: 40px;
        height: 40px;
    }
    
    /* Upload label 스타일 */
    .upload-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--enhanced-text);
        margin-bottom: 0.25rem;
        text-align: center;
    }
    
    .character-top-controls {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        width: 100%;
    }

    .sprite-animation-controls {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
    }

    .character-advanced-wrapper {
        width: 100%;
        margin-top: 1.5rem;
    }

    .search-panel {
        width: 100%;
        background: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 1.25rem 1.5rem;
        box-shadow: var(--enhanced-shadow);
    }

    .character-upload-row,
    .sprite-animation-controls,
    .enhanced-search-box {
        gap: 1rem;
    }

    /* Sprites 탭 hero 텍스트 여백 추가 */
    #character-sprites-tab .enhanced-welcome-text,
    #sprite-animation-tab .enhanced-welcome-text {
        margin-top: 2rem;
        margin-bottom: 3rem;
    }

    /* 로그인 오버레이 UI 제거됨 (Next.js에서 로그인 처리) */

    #user-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1rem 0;
    }

    .token-display {
        font-size: 1rem;
        font-weight: 600;
        color: var(--enhanced-text);
    }

    #last-image-preview {
        max-width: 360px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    """
    
    # JavaScript for postMessage token updates and auto-login
    TOKEN_UPDATE_JS = """
    <script>
    (function() {
        // Extract token count from token display text
        function extractTokenCount(text) {
            if (!text) return null;
            const match = text.match(/Tokens Remaining:\\s*\\*\\*(\\d+)\\*\\*/);
            return match ? parseInt(match[1], 10) : null;
        }
        
        // Send token update to parent window (if in iframe)
        function sendTokenUpdate(tokenCount) {
            if (window.parent && window.parent !== window && tokenCount !== null) {
                window.parent.postMessage({
                    type: 'token-updated',
                    tokens: tokenCount
                }, '*');
            }
        }
        
        // 로그인 오버레이 UI가 제거되었으므로 이 함수는 더 이상 필요 없음
        // 하지만 사용자 메타 행 표시는 유지
        function ensureUserMetaRowVisible() {
            const userMetaRow = document.querySelector('#user-meta-row');
            if (userMetaRow) {
                userMetaRow.style.cssText = 'display: flex !important; visibility: visible !important;';
            }
        }
        
        // Get token count from Gradio component value (even if hidden)
        function getTokenFromComponent() {
            // Try to find token display component by ID pattern
            const tokenComponent = document.querySelector('[id*="token-display"], [id*="token_display"]');
            if (tokenComponent) {
                // Try to get value from Gradio component's internal state
                const gradioApp = document.querySelector('gradio-app');
                if (gradioApp && gradioApp.__gradio_app__) {
                    try {
                        // Access Gradio's component registry
                        const components = gradioApp.__gradio_app__.get_components();
                        for (let comp of components) {
                            if (comp.props && comp.props.elem_id && comp.props.elem_id.includes('token')) {
                                const value = comp.props.value || comp.value;
                                if (value) {
                                    const tokenCount = extractTokenCount(value);
                                    if (tokenCount !== null) {
                                        return tokenCount;
                                    }
                                }
                            }
                        }
                    } catch (e) {
                        console.log('[Token Update] Could not access Gradio components:', e);
                    }
                }
                // Fallback: try to read from text content
                const text = tokenComponent.textContent || tokenComponent.innerText || '';
                return extractTokenCount(text);
            }
            return null;
        }
        
        // Monitor token display updates and Gradio component changes
        function observeTokenDisplay() {
            let lastTokenCount = null;
            
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' || mutation.type === 'characterData') {
                        // Try to get token from component
                        const tokenCount = getTokenFromComponent();
                        if (tokenCount !== null && tokenCount !== lastTokenCount) {
                            lastTokenCount = tokenCount;
                            sendTokenUpdate(tokenCount);
                        }
                        
                        // Also try to find visible token elements
                        const tokenElements = document.querySelectorAll('[id*="token"], .token-display, markdown');
                        tokenElements.forEach(function(el) {
                            const text = el.textContent || el.innerText || '';
                            const tokenCount = extractTokenCount(text);
                            if (tokenCount !== null && tokenCount !== lastTokenCount) {
                                lastTokenCount = tokenCount;
                                sendTokenUpdate(tokenCount);
                            }
                        });
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                characterData: true,
                attributes: true,
                attributeFilter: ['value', 'data-value']
            });
            
            // Poll for token updates (fallback method)
            setInterval(function() {
                const tokenCount = getTokenFromComponent();
                if (tokenCount !== null && tokenCount !== lastTokenCount) {
                    lastTokenCount = tokenCount;
                    sendTokenUpdate(tokenCount);
                }
                
                // Also check visible elements
                const tokenElements = document.querySelectorAll('[id*="token"], .token-display, markdown');
                tokenElements.forEach(function(el) {
                    const text = el.textContent || el.innerText || '';
                    const tokenCount = extractTokenCount(text);
                    if (tokenCount !== null && tokenCount !== lastTokenCount) {
                        lastTokenCount = tokenCount;
                        sendTokenUpdate(tokenCount);
                    }
                });
            }, 500);
        }
        
        // Listen for Gradio component updates
        function setupGradioListener() {
            // Listen for custom events or Gradio updates
            document.addEventListener('gradio:component-update', function(e) {
                if (e.detail && e.detail.id && e.detail.id.includes('token')) {
                    const tokenCount = extractTokenCount(e.detail.value || '');
                    if (tokenCount !== null) {
                        sendTokenUpdate(tokenCount);
                    }
                }
            });
            
            // Monitor Gradio app updates
            const gradioApp = document.querySelector('gradio-app');
            if (gradioApp) {
                const observer = new MutationObserver(function() {
                    const tokenCount = getTokenFromComponent();
                    if (tokenCount !== null) {
                        sendTokenUpdate(tokenCount);
                    }
                });
                observer.observe(gradioApp, {
                    childList: true,
                    subtree: true,
                    attributes: true
                });
            }
        }
        
        // Initialize when DOM is ready
        function init() {
            // 사용자 메타 행 표시
            ensureUserMetaRowVisible();
            setTimeout(ensureUserMetaRowVisible, 100);
            setTimeout(ensureUserMetaRowVisible, 500);
            
            observeTokenDisplay();
            setupGradioListener();
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        // window.load 이벤트에서도 실행
        window.addEventListener('load', function() {
            setTimeout(ensureUserMetaRowVisible, 100);
            setTimeout(ensureUserMetaRowVisible, 500);
            setTimeout(init, 1000); // Re-initialize after Gradio loads
        });
    })();
    </script>
    """
    
    with gr.Blocks(
        title="Sprite Studio", 
        theme=gr.themes.Soft(),
        css=ENHANCED_STYLE_CSS
    ) as demo:
        gr.HTML("""
        <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
        """ + TOKEN_UPDATE_JS)
        gr.Markdown("# Sprite Studio", elem_classes=["app-title"])
        gr.Markdown("By Jian Lee", elem_classes=["app-subtitle"])

        user_session_state = gr.State(_default_user_session())
        
        # Hidden input for token (JavaScript에서 채움) - 모든 이벤트에서 사용하기 위해 여기서 정의
        token_input = gr.Textbox(visible=False, value="", label="")

        with gr.Row(elem_id="user-meta-row", visible=False) as user_meta_row:
            token_display = gr.Markdown(
                "Sign in to start generating assets.",
                elem_classes=["token-display"]
            )
            logout_button = gr.Button("Sign Out", variant="secondary")

        last_image_preview = gr.Image(
            label="Last Generated Image",
            visible=False,
            elem_id="last-image-preview"
        )

        # 로그인/회원가입 UI 제거 (Next.js에서 이미 로그인 처리)
        # 토큰은 쿼리스트링으로 전달받아 자동 검증
        auth_status = gr.Markdown("", elem_id="auth-status", visible=False)

        # gradio 5 uses the function gr.update(...) but does not expose a gr.Update type.
        # Using a dict return type here avoids an AttributeError at import time.
        def _token_component_update_from_state(session: Dict) -> Dict:
            # Hidden but value is updated so JavaScript can read it
            tokens = session.get("tokens", 0)
            return gr.update(value=_format_token_text(tokens), visible=False)

        def _last_image_component_update_from_state(session: Dict) -> Dict:
            # Always hidden - last image preview disabled
            return gr.update(value=None, visible=False)

        def handle_sign_up(email: str, password: str):
            if not email or not password:
                return "❌ Enter email and password to create an account."
            try:
                sign_up_user(email, password)
                return "✅ Account created! Please verify your email before signing in."
            except Exception as exc:  # noqa: BLE001
                return f"❌ {str(exc)}"

        def handle_sign_in(email: str, password: str, session: Dict):
            if not email or not password:
                return (
                    "❌ Enter email and password.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    session,
                )
            try:
                response = sign_in_user(email, password)
                auth_session = getattr(response, "session", None)
                user_meta = getattr(response, "user", None)
            except Exception as exc:  # noqa: BLE001
                return (
                    f"❌ {str(exc)}",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    session,
                )

            if not auth_session or not user_meta:
                return (
                    "❌ Failed to sign in. Please try again.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    session,
                )

            user_id = getattr(user_meta, "id", None)
            if not user_id:
                return (
                    "❌ Missing user information from Supabase.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    session,
                )

            tokens = ensure_user_token_balance(user_id)
            last_url = get_last_generated_image_url(user_id)
            updated_session = {
                "authenticated": True,
                "user_id": user_id,
                "email": getattr(user_meta, "email", email),
                "access_token": getattr(auth_session, "access_token", None),
                "tokens": tokens,
                "last_image_url": last_url,
            }

            return (
                f"✅ Logged in as {updated_session['email']}",
                gr.update(value=_format_token_text(tokens), visible=True),
                gr.update(value=last_url, visible=bool(last_url)),
                gr.update(visible=False),
                gr.update(visible=True),
                updated_session,
            )

        def handle_auto_login_from_token(token: str):
            """쿼리스트링의 토큰으로 자동 로그인 (UI 없이)"""
            print(f"[Auto-login] Function called with token: {token[:20] if token else 'None'}...")
            
            if not token or token.strip() == "":
                print("[Auto-login] No token provided - keeping existing session")
                # 토큰이 없으면 기존 세션 유지 (아무것도 변경하지 않음)
                return (
                    gr.update(),  # auth_status 변경 없음
                    gr.update(),  # token_display 변경 없음
                    gr.update(),  # last_image_preview 변경 없음
                    gr.update(),  # user_meta_row 변경 없음
                    gr.update(),  # user_session_state 변경 없음
                    gr.update(),  # token_input 변경 없음
                )
            
            # 토큰이 있을 때만 새 세션 시작
            session = _default_user_session()
            
            try:
                print(f"[Auto-login] Validating token...")
                # 토큰 검증
                claims = validate_access_token(token.strip())
                user_id = claims.get("sub")
                
                if not user_id:
                    raise ValueError("Invalid token: no user ID")
                
                print(f"[Auto-login] Token validated, user_id: {user_id}")
                
                # 토큰 잔액 확인 및 초기화
                tokens = ensure_user_token_balance(user_id)
                last_image_url = get_last_generated_image_url(user_id)
                
                print(f"[Auto-login] User tokens: {tokens}, last_image: {last_image_url}")
                
                # 세션 업데이트
                updated_session = {
                    "authenticated": True,
                    "user_id": user_id,
                    "tokens": tokens,
                    "last_image_url": last_image_url,
                    "access_token": token.strip(),
                }
                
                print("[Auto-login] Auto-login successful")
                
                return (
                    "",  # auth_status (빈 문자열 = 성공, 메시지 없음)
                    _token_component_update_from_state(updated_session),
                    _last_image_component_update_from_state(updated_session),
                    gr.update(visible=False),   # user_meta_row 숨기기 (Next.js에서 표시)
                    updated_session,
                    token.strip()  # token_input에 저장
                )
            except Exception as exc:  # noqa: BLE001
                # 토큰 검증 실패 시 에러 메시지 표시
                print(f"[Auto-login] Token validation failed: {exc}")
                return (
                    f"⚠️ Authentication failed: {str(exc)}. Please refresh the page.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    gr.update(visible=False),  # user_meta_row 숨기기
                    session,
                    ""  # token_input (빈 값)
                )

        def handle_sign_out(session: Dict):
            try:
                sign_out_user()
            except Exception:
                pass
            return (
                "👋 Signed out successfully.",
                gr.update(value="Sign in to start generating assets.", visible=False),
                gr.update(value=None, visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
                _default_user_session(),
            )

        with gr.Tab("Item", elem_id="item-generation-tab"):
            with gr.Column(elem_classes=["enhanced-center-container"]):
                item_hero = gr.Markdown(
                    "## What kind of item do you want to forge today?",
                    elem_classes=["enhanced-welcome-text"]
                )
                item_output = gr.Image(
                    label="",
                    show_label=False,
                    visible=False,
                    elem_classes=["enhanced-image-container"]
                )
            
            with gr.Accordion("⚙️ Advanced Settings", open=False, elem_classes=["enhanced-advanced-settings"]):
                gr.Markdown("### 🎨 Style Preferences")
                with gr.Row():
                    with gr.Column():
                        item_art_style = gr.Dropdown(choices=DEFAULT_CHOICES + ART_STYLES, value="None", label="Art Style")
                        item_mood = gr.Dropdown(choices=DEFAULT_CHOICES + MOOD_OPTIONS, value="None", label="Overall Mood")
                        item_color_palette = gr.Dropdown(choices=DEFAULT_CHOICES + COLOR_PALETTES, value="None", label="Color Palette")
                    with gr.Column():
                        item_line_style = gr.Dropdown(choices=DEFAULT_CHOICES + LINE_STYLES, value="None", label="Line Art Style")
                        item_composition = gr.Dropdown(choices=DEFAULT_CHOICES + COMPOSITION_STYLES, value="None", label="Composition Style")
                
                item_additional_notes = gr.Textbox(
                    label="Additional Style Notes",
                    placeholder="Any specific style preferences or artistic directions...",
                    lines=3
                )
                
                item_image_width, item_image_height, item_lock_aspect_ratio, item_use_percentage = create_image_size_controls()
                
                with gr.Group():
                    gr.Markdown("### ⚙️ Load Settings")
                    with gr.Row():
                        item_config_dropdown = create_config_dropdown(initial_configs)
                        item_load_config_btn = gr.Button("📂 Load Settings", variant="secondary", size="sm")
            
            with gr.Row(elem_classes=["enhanced-search-container"]):
                with gr.Column():
                    with gr.Column(elem_classes=["search-panel"]):
                        with gr.Row(elem_classes=["enhanced-search-box"]):
                            item_reference_image = create_reference_upload(
                                label="Upload Style Reference",
                                elem_id="item-style-reference-upload",
                                elem_classes=["reference-plus-upload"],
                                show_label=False
                            )
                            
                            item_description = gr.Textbox(
                                label="",
                                placeholder="Describe your item...",
                                show_label=False,
                                lines=1,
                                elem_classes=["enhanced-search-input"],
                                container=False,
                                scale=8
                            )
                            
                            generate_item_btn = gr.Button(
                                "Generate",
                                elem_classes=["enhanced-generate-btn"],
                                size="sm",
                                scale=2,
                                variant="primary"
                            )
            
            item_status = gr.Textbox(
                label="Status",
                value="Ready to generate item...",
                interactive=False,
                visible=False
            )
            
            item_prompt_display = gr.Textbox(
                label="Complete Prompt",
                value="Describe your item to see the generated prompt...",
                lines=8,
                interactive=False,
                show_copy_button=True,
                visible=False
            )
                        
        with gr.Tab("Character", elem_id="character-creation-tab"):
            
            # Pixel Mode 선택 버튼 (탭 바로 아래 좌측)
            with gr.Row(elem_classes=["character-top-controls"]):
                with gr.Row(elem_classes=["enhanced-pixel-mode-toggle"]):
                    character_mode = gr.Checkbox(
                        label="Pixel Mode",
                        value=False,
                        elem_id="char-pixel-mode-checkbox"
                    )
            
            # 메인 히어로 영역
            with gr.Column(elem_classes=["enhanced-center-container"]):
                # "What do you want to create today?" 문구
                welcome_text = gr.Markdown(
                    "## What do you want to create today?",
                    elem_classes=["enhanced-welcome-text"],
                    visible=True
                )
                
                # 생성된 이미지 (초기에는 숨김)
                character_output = gr.Image(
                    label="",
                    show_label=False,
                    visible=False,
                    elem_classes=["enhanced-image-container"]
                )
                        
            # 하단 고정 검색창
            with gr.Row(elem_classes=["enhanced-search-container"]):
                with gr.Column():
                    with gr.Column(elem_classes=["search-panel"]):
                        with gr.Row(elem_classes=["character-upload-row"]):
                            with gr.Column(scale=2, min_width=140):
                                gr.Markdown("**Character**", elem_classes=["upload-label"])
                                character_reference_image = create_reference_upload(
                                    label="Upload Character Reference",
                                    elem_id="char-reference-image-upload",
                                    elem_classes=["reference-plus-upload"],
                                    show_label=False
                                )
                            with gr.Column(scale=2, min_width=140):
                                gr.Markdown("**Item**", elem_classes=["upload-label"])
                                item_reference_image = create_reference_upload(
                                    label="Upload Item Reference",
                                    elem_id="item-reference-image-upload",
                                    elem_classes=["reference-plus-upload"],
                                    show_label=False
                                )
                            with gr.Column(scale=4, min_width=220):
                                character_description = gr.Textbox(
                                    label="",
                                    placeholder="Describe what you want to create...",
                                    show_label=False,
                                    lines=1,
                                    elem_classes=["enhanced-search-input"],
                                    container=False
                                )
                            with gr.Column(scale=2, min_width=150):
                                generate_character_btn = gr.Button(
                                    "Generate",
                                    elem_classes=["enhanced-generate-btn"],
                                    size="sm",
                                    variant="primary"
                                )
            
            # Backward compatibility - keep for now but not used
            character_item_image = gr.File(
                label="",
                file_types=FILE_TYPES,
                            visible=False
            )
            
            # Alias for backward compatibility
            reference_image = character_reference_image
            
            # Status display (숨김)
            character_status = gr.Textbox(
                label="",
                value="Ready to generate character...",
                interactive=False,
                visible=False
            )
            
            # Generate 버튼은 검색창 오른쪽에 이미 추가됨 (위에서 생성)
            
            # 프롬프트 미리보기 컴포넌트 (숨김, 이벤트 핸들러용)
            character_prompt_display = gr.Textbox(
                label="",
                value="",
                visible=False,
                interactive=False
            )

            with gr.Column(elem_classes=["character-advanced-wrapper"]):
                char_advanced_settings = gr.Accordion("⚙️ Advanced Settings", open=False, elem_classes=["enhanced-advanced-settings"], elem_id="char-advanced-settings")
                with char_advanced_settings:
                    style_preferences_group = gr.Group(visible=True)
                    with style_preferences_group:
                        gr.Markdown("### 🎨 Style Preferences")
                        with gr.Row():
                            with gr.Column():
                                art_style = gr.Dropdown(choices=DEFAULT_CHOICES + ART_STYLES, value="None", label="Art Style")
                                mood = gr.Dropdown(choices=DEFAULT_CHOICES + MOOD_OPTIONS, value="None", label="Overall Mood")
                                color_palette = gr.Dropdown(choices=DEFAULT_CHOICES + COLOR_PALETTES, value="None", label="Color Palette")
                            with gr.Column():
                                character_style = gr.Dropdown(choices=DEFAULT_CHOICES + CHARACTER_STYLES, value="None", label="Character Style")
                                line_style = gr.Dropdown(choices=DEFAULT_CHOICES + LINE_STYLES, value="None", label="Line Art Style")
                                composition = gr.Dropdown(choices=DEFAULT_CHOICES + COMPOSITION_STYLES, value="None", label="Composition Style")

                    additional_notes = gr.Textbox(
                        label="Additional Style Notes",
                        placeholder="Any specific style preferences or artistic directions...",
                        lines=3
                    )

                    image_size_group = gr.Group(visible=True)
                    with image_size_group:
                        char_image_width, char_image_height, char_lock_aspect_ratio, char_use_percentage = create_image_size_controls()

                    with gr.Group():
                        gr.Markdown("### ⚙️ Load Settings")
                        with gr.Row():
                            char_config_dropdown = create_config_dropdown(initial_configs)
                            char_load_config_btn = gr.Button("📂 Load Settings", variant="secondary", size="sm")
        
        with gr.Tab("Sprites", elem_id="character-sprites-tab"):
            with gr.Column(elem_classes=["enhanced-center-container"]):
                sprites_hero = gr.Markdown(
                    "## Animate your hero’s next move",
                    elem_classes=["enhanced-welcome-text"]
                )
                sprites_gallery = gr.Gallery(
                    label="",
                    show_label=False,
                    columns=3,
                    rows=2,
                    height="auto",
                    allow_preview=True,
                    elem_classes=["enhanced-image-container"]
                )
                sprites_status = gr.Textbox(
                    label="Status",
                    value="Describe a character and actions to start generating sprites.",
                    interactive=False,
                    visible=False
                )
            
            with gr.Accordion("⚙️ Advanced Settings", open=False, elem_classes=["enhanced-advanced-settings"]):
                gr.Markdown("### 🎨 Style Preferences")
                with gr.Row():
                    with gr.Column():
                        sprite_art_style = gr.Dropdown(choices=DEFAULT_CHOICES + ART_STYLES, value="None", label="Art Style")
                        sprite_mood = gr.Dropdown(choices=DEFAULT_CHOICES + MOOD_OPTIONS, value="None", label="Overall Mood")
                        sprite_color_palette = gr.Dropdown(choices=DEFAULT_CHOICES + COLOR_PALETTES, value="None", label="Color Palette")
                    with gr.Column():
                        sprite_character_style = gr.Dropdown(choices=DEFAULT_CHOICES + CHARACTER_STYLES, value="None", label="Character Style")
                        sprite_line_style = gr.Dropdown(choices=DEFAULT_CHOICES + LINE_STYLES, value="None", label="Line Art Style")
                        sprite_composition = gr.Dropdown(choices=DEFAULT_CHOICES + COMPOSITION_STYLES, value="None", label="Composition Style")
                
                sprite_additional_notes = gr.Textbox(
                    label="Additional Style Notes",
                    placeholder="Any specific style preferences or artistic directions...",
                    lines=2
                )
                
                sprite_image_width, sprite_image_height, sprite_lock_aspect_ratio, sprite_use_percentage = create_image_size_controls()
                
                with gr.Group():
                    gr.Markdown("### ⚙️ Load Settings")
                    with gr.Row():
                        sprite_config_dropdown = create_config_dropdown(initial_configs)
                        sprite_load_config_btn = gr.Button("📂 Load Settings", variant="secondary", size="sm")
                        
            with gr.Row(elem_classes=["enhanced-search-container"]):
                with gr.Column():
                    with gr.Column(elem_classes=["search-panel"]):
                        with gr.Row(elem_classes=["enhanced-search-box"]):
                            sprite_reference_image = create_reference_upload(
                                label="Upload Character Reference",
                                elem_id="sprite-reference-upload",
                                elem_classes=["reference-plus-upload"],
                                show_label=False
                            )
                            
                            sprite_character_description = gr.Textbox(
                                label="",
                                placeholder="Describe your character...",
                                show_label=False,
                                lines=1,
                                elem_classes=["enhanced-search-input"],
                                container=False,
                                scale=5
                            )
                            
                            actions_text = gr.Textbox(
                                label="",
                                placeholder="Actions (idle, run, jump...)",
                                show_label=False,
                                lines=1,
                                elem_classes=["enhanced-search-input"],
                                container=False,
                                scale=3
                            )
                            
                            generate_sprites_btn = gr.Button(
                                "Generate",
                                elem_classes=["enhanced-generate-btn"],
                                size="sm",
                                scale=2,
                                variant="primary"
                            )
            
            sprites_prompt_display = gr.Textbox(
                label="Complete Prompt",
                value="Provide a character description and actions to preview the generated prompt.",
                lines=6,
                interactive=False,
                show_copy_button=True,
                visible=False
            )
        
        with gr.Tab("Sprite Animation", elem_id="sprite-animation-tab"):
            with gr.Column(elem_classes=["enhanced-center-container"]):
                sprite_anim_hero = gr.Markdown(
                    "## Build cinematic sprite animations",
                    elem_classes=["enhanced-welcome-text"]
                )
                sprite_gallery = gr.Gallery(
                    label="",
                    show_label=False,
                    columns=3,
                    rows=2,
                    height="auto",
                    allow_preview=True,
                    elem_classes=["enhanced-image-container"]
                )
                sprite_status = gr.Textbox(
                    label="Status",
                    value="Select an animation type and upload a character reference to begin.",
                    interactive=False,
                    visible=False
                )
                with gr.Row():
                    download_zip_btn = gr.Button("Download All Frames as ZIP", variant="secondary", size="sm")
                    sprite_zip_download = gr.File(
                        label="Download ZIP File",
                        visible=False
                    )
                    sprite_zip_status = gr.Textbox(
                        label="ZIP Status",
                        value="Generate sprites first, then click the download button.",
                        interactive=False,
                        visible=False
                    )
                animation_info = gr.Markdown(default_animation_text)
                frame_info = gr.Markdown(default_frame_text)
            
            with gr.Row(elem_classes=["enhanced-search-container"]):
                with gr.Column():
                    with gr.Column(elem_classes=["search-panel"]):
                        with gr.Row(elem_classes=["sprite-animation-controls"]):
                            with gr.Column(scale=2, min_width=140):
                                gr.Markdown("**Character**", elem_classes=["upload-label"])
                                enhanced_sprite_reference_image = create_reference_upload(
                                    label="Upload Character Image",
                                    elem_id="enhanced-sprite-reference-upload",
                                    elem_classes=["reference-plus-upload"],
                                    show_label=False
                                )
                            with gr.Column(scale=3, min_width=200):
                                action_type_dropdown = gr.Dropdown(
                                    choices=["Attack", "Jump", "Walk", "Dead"],
                                    value="Attack",
                                    label="Animation Mode",
                                    show_label=False
                                )
                            with gr.Column(scale=2, min_width=150):
                                generate_sprite_btn = gr.Button(
                                    "Generate",
                                    elem_classes=["enhanced-generate-btn"],
                                    size="sm",
                                    variant="primary"
                                )
        
        with gr.Tab("Background", elem_id="background-tab"):
            with gr.Column(elem_classes=["enhanced-center-container"]):
                background_hero = gr.Markdown(
                    "## Craft immersive worlds",
                    elem_classes=["enhanced-welcome-text"]
                )
                background_output = gr.Image(
                    label="",
                    show_label=False,
                    visible=False,
                    elem_classes=["enhanced-image-container"]
                )
                background_status = gr.Textbox(
                    label="Status",
                    value="Describe a scene to start generating backgrounds.",
                    interactive=False,
                    visible=False
                )
            
            with gr.Accordion("⚙️ Advanced Settings", open=False, elem_classes=["enhanced-advanced-settings"]):
                orientation = gr.Radio(
                    choices=["landscape", "portrait"],
                    value="landscape",
                    label="Orientation"
                )
                
                gr.Markdown("### 🎨 Style Preferences")
                with gr.Row():
                    with gr.Column():
                        bg_art_style = gr.Dropdown(choices=DEFAULT_CHOICES + ART_STYLES, value="None", label="Art Style")
                        bg_mood = gr.Dropdown(choices=DEFAULT_CHOICES + MOOD_OPTIONS, value="None", label="Overall Mood")
                        bg_color_palette = gr.Dropdown(choices=DEFAULT_CHOICES + COLOR_PALETTES, value="None", label="Color Palette")
                    with gr.Column():
                        bg_line_style = gr.Dropdown(choices=DEFAULT_CHOICES + LINE_STYLES, value="None", label="Line Art Style")
                        bg_composition = gr.Dropdown(choices=DEFAULT_CHOICES + COMPOSITION_STYLES, value="None", label="Composition Style")
                
                bg_additional_notes = gr.Textbox(
                    label="Additional Style Notes",
                    placeholder="Any specific style preferences or artistic directions...",
                    lines=3
                )
                
                bg_image_width, bg_image_height, bg_lock_aspect_ratio, bg_use_percentage = create_image_size_controls()
                
                with gr.Group():
                    gr.Markdown("### ⚙️ Load Settings")
                    with gr.Row():
                        bg_config_dropdown = create_config_dropdown(initial_configs)
                        bg_load_config_btn = gr.Button("📂 Load Settings", variant="secondary", size="sm")
                    
            with gr.Row(elem_classes=["enhanced-search-container"]):
                with gr.Column():
                    with gr.Column(elem_classes=["search-panel"]):
                        with gr.Row(elem_classes=["enhanced-search-box"]):
                            background_description = gr.Textbox(
                                label="",
                                placeholder="Describe your background...",
                                show_label=False,
                                lines=1,
                                elem_classes=["enhanced-search-input"],
                                container=False,
                                scale=8
                            )
                            
                            generate_background_btn = gr.Button(
                                "Generate",
                                elem_classes=["enhanced-generate-btn"],
                                size="sm",
                                scale=2,
                                variant="primary"
                            )
            
            background_prompt_display = gr.Textbox(
                label="Complete Prompt",
                value="Describe a background to preview the generated prompt...",
                lines=6,
                interactive=False,
                show_copy_button=True,
                visible=False
            )
        
        with gr.Tab("Settings"):
            gr.Markdown("### 💾 Save and Load Style Settings")
            gr.Markdown("Save and load frequently used style settings for reuse.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Saved Settings Load")
                    load_config_dropdown = create_config_dropdown(initial_configs)
                    
                    load_config_btn = gr.Button("📂 Load Settings", variant="secondary")
                    
                    load_status = gr.Textbox(
                        label="Status",
                        value="Select a setting and click the load button.",
                        interactive=False
                    )
                    
                    gr.Markdown("#### Delete Settings")
                    delete_config_dropdown = create_config_dropdown(initial_configs, "Select a setting to delete")
                    
                    delete_config_btn = gr.Button("🗑️ Delete Settings", variant="stop")
                    
                    delete_status = gr.Textbox(
                        label="Delete Status",
                        value="Select a setting to delete.",
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("#### Save Current Settings")
                    gr.Markdown("You can save the current settings by adjusting the settings below.")
                    
                    # 저장용 설정 입력 필드들
                    save_config_name = gr.Textbox(
                        label="Setting Name",
                        placeholder="e.g. My Basic Style, Fantasy Style, Pixel Art, etc.",
                        lines=1
                    )
                    
                    with gr.Row():
                        with gr.Column():
                            save_art_style = gr.Dropdown(choices=DEFAULT_CHOICES + ART_STYLES, value="None", label="Art Style")
                            save_mood = gr.Dropdown(choices=DEFAULT_CHOICES + MOOD_OPTIONS, value="None", label="Overall Mood")
                            save_color_palette = gr.Dropdown(choices=DEFAULT_CHOICES + COLOR_PALETTES, value="None", label="Color Palette")
                        with gr.Column():
                            save_character_style = gr.Dropdown(choices=DEFAULT_CHOICES + CHARACTER_STYLES, value="None", label="Character Style")
                            save_line_style = gr.Dropdown(choices=DEFAULT_CHOICES + LINE_STYLES, value="None", label="Line Art Style")
                            save_composition = gr.Dropdown(choices=DEFAULT_CHOICES + COMPOSITION_STYLES, value="None", label="Composition Style")
                    
                    save_additional_notes = gr.Textbox(
                        label="Additional Style Notes",
                        placeholder="Additional style notes...",
                        lines=3
                    )
                    
                    save_config_btn = gr.Button("💾 Save Settings", variant="primary", size="lg")
                    
                    save_status = gr.Textbox(
                        label="Save Status",
                        value="Enter the settings and click the save button.",
                        interactive=False
                    )
            
            gr.Markdown("### 📋 Usage")
            gr.Markdown("""
            1. **Save Settings**: Adjust the settings fields to your desired values, enter the setting name, and click the 'Save Settings' button.
            2. **Load Settings**: Select a setting from the saved settings list and click the 'Load Settings' button.
            3. **Delete Settings**: Select a setting you no longer need and click the 'Delete Settings' button.
            """)
        
        # 이벤트 핸들러 설정
        _setup_event_handlers(
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
            char_image_width, char_image_height, char_lock_aspect_ratio, char_use_percentage,
            sprite_image_width, sprite_image_height, sprite_lock_aspect_ratio, sprite_use_percentage,
            bg_image_width, bg_image_height, bg_lock_aspect_ratio, bg_use_percentage,
            item_image_width, item_image_height, item_lock_aspect_ratio, item_use_percentage
        )
        
        # 모드 변경 시 UI 업데이트 함수 제거
        # Advanced Settings와 픽셀 모드는 이제 독립적으로 작동
        # Advanced Settings는 Accordion으로 열고 닫을 수 있고,
        # 픽셀 모드 선택은 생성 로직에서만 영향을 미침
        
            # 생성 버튼 래퍼 함수 (제미나이 스타일 UI 업데이트 포함)
        def generate_character_wrapper(character_mode, character_description, art_style, mood, color_palette, 
                                      character_style, line_style, composition, additional_notes, 
                                      character_reference_image, item_reference_image, 
                                      char_image_width, char_image_height, char_lock_aspect_ratio, char_use_percentage,
                                      user_session, access_token):
            """모드에 따라 적절한 생성 함수 호출하고 UI 업데이트"""
            print(f"[Generate Character] user_session received: {user_session}")
            print(f"[Generate Character] access_token received: {access_token[:20] if access_token else 'None'}...")
            session = user_session or _default_user_session()
            
            # 세션이 인증되지 않았지만 토큰이 있으면 직접 인증 시도
            if not session.get("authenticated") and access_token and access_token.strip():
                print("[Generate Character] Session not authenticated, trying direct token validation...")
                try:
                    claims = validate_access_token(access_token.strip())
                    user_id = claims.get("sub")
                    if user_id:
                        tokens = ensure_user_token_balance(user_id)
                        session = {
                            "authenticated": True,
                            "user_id": user_id,
                            "tokens": tokens,
                            "access_token": access_token.strip(),
                        }
                        print(f"[Generate Character] Direct auth success: user_id={user_id}, tokens={tokens}")
                except Exception as e:
                    print(f"[Generate Character] Direct auth failed: {e}")
            
            print(f"[Generate Character] Final session: authenticated={session.get('authenticated')}, user_id={session.get('user_id')}, tokens={session.get('tokens')}")
            if not session.get("authenticated"):
                return [
                    gr.update(visible=True),
                    gr.update(visible=False),
                    "Please sign in to generate characters.",
                    gr.update(),
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if session.get("tokens", 0) <= 0:
                return [
                    gr.update(visible=True),
                    gr.update(visible=False),
                    "You have no tokens remaining.",
                    gr.update(),
                    gr.update(value=_format_token_text(0), visible=True),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if not character_description or not character_description.strip():
                return [
                    gr.update(visible=True),  # welcome_text
                    gr.update(visible=False),  # character_output
                    "Please enter a character description.",
                    gr.update(),  # char_advanced_settings (변경 없음)
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]
            
            def _sanitize_pref(value):
                if not value:
                    return None
                value = str(value).strip()
                if not value or value == "None":
                    return None
                return value
            
            # 이미지 생성 (character_mode는 이제 boolean)
            if character_mode is True:  # Pixel Mode가 명확히 체크되어 있으면
                # 스타일 요약을 설명에 포함
                style_parts = []
                pref_map = [
                    ("Art Style", art_style),
                    ("Mood", mood),
                    ("Color Palette", color_palette),
                    ("Character Style", character_style),
                    ("Line Style", line_style),
                    ("Composition", composition),
                ]
                for label, val in pref_map:
                    clean = _sanitize_pref(val)
                    if clean:
                        style_parts.append(f"{label}: {clean}")
                
                additional_notes_clean = _sanitize_pref(additional_notes)
                
                pixel_description = character_description.strip()
                if style_parts:
                    pixel_description += "\nStyle preferences: " + ", ".join(style_parts)
                if additional_notes_clean:
                    pixel_description += f"\nAdditional notes: {additional_notes_clean}"
                
                # Pixel generator에 reference images 전달
                status, img_path = generate_pixel_character(
                    pixel_description,
                    character_reference_image,
                    item_reference_image
                )
            else:
                # Normal Mode: 기존 generate_character_interface 호출 (pixel mode가 명확히 False일 때만)
                if char_image_width:
                    img_path, status = generate_character_interface(
                        character_description, art_style, mood, color_palette, character_style, 
                        line_style, composition, additional_notes, character_reference_image, item_reference_image,
                        char_image_width, char_image_height, char_lock_aspect_ratio, char_use_percentage
                    )
                else:
                    img_path, status = generate_character_interface(
                        character_description, art_style, mood, color_palette, character_style, 
                        line_style, composition, additional_notes, character_reference_image, item_reference_image
                    )
            
            # 이미지가 생성되었으면 welcome_text 숨기고 이미지 표시
            token_update = _token_component_update_from_state(session)
            last_image_update = _last_image_component_update_from_state(session)

            if img_path:
                try:
                    remaining = consume_user_token(session["user_id"])
                    session["tokens"] = remaining
                    metadata = {
                        "description": character_description,
                        "pixel_mode": bool(character_mode),
                        "art_style": art_style,
                        "mood": mood,
                        "color_palette": color_palette,
                    }
                    public_url = record_generated_image(
                        session["user_id"],
                        "character",
                        img_path,
                        metadata=metadata,
                    )
                    session["last_image_url"] = public_url
                    token_update = gr.update(value=_format_token_text(remaining), visible=True)
                    last_image_update = gr.update(value=public_url, visible=True)
                except Exception as logging_error:  # noqa: BLE001
                    print(f"[Character] Failed to record image: {logging_error}")

                return [
                    gr.update(visible=False),  # welcome_text
                    gr.update(value=img_path, visible=True),  # character_output
                    status,
                    gr.update(open=False),  # char_advanced_settings 닫기
                    token_update,
                    last_image_update,
                    session,
                ]
            else:
                return [
                    gr.update(visible=True),  # welcome_text
                    gr.update(visible=False),  # character_output
                    status,
                    gr.update(open=False),  # char_advanced_settings 닫기
                    token_update,
                    last_image_update,
                    session,
                ]
        
        # 파일 업로드 이벤트 핸들러는 reference_image 컴포넌트에 직접 연결됨
        # + 버튼 클릭 시 reference_image의 파일 입력이 트리거됨
        
        # Advanced Settings는 이제 Accordion이므로 별도 이벤트 핸들러 불필요
        
        # 검색창에서 Enter 키로 생성 시작
        character_description.submit(
            fn=generate_character_wrapper,
            inputs=[character_mode, character_description, art_style, mood, color_palette, character_style, 
                    line_style, composition, additional_notes, character_reference_image, item_reference_image,
                    char_image_width, char_image_height, char_lock_aspect_ratio, char_use_percentage, user_session_state, token_input],
            outputs=[welcome_text, character_output, character_status, char_advanced_settings, token_display, last_image_preview, user_session_state]
        ).then(
            fn=None,
            inputs=[user_session_state],
            js="""
            function(session) {
                if (session && session.tokens !== undefined && window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'token-updated',
                        tokens: session.tokens
                    }, '*');
                }
            }
            """
        )
        
        # 생성 버튼 이벤트 핸들러
        generate_character_btn.click(
            fn=generate_character_wrapper,
            inputs=[character_mode, character_description, art_style, mood, color_palette, character_style, 
                    line_style, composition, additional_notes, character_reference_image, item_reference_image,
                    char_image_width, char_image_height, char_lock_aspect_ratio, char_use_percentage, user_session_state, token_input],
            outputs=[welcome_text, character_output, character_status, char_advanced_settings, token_display, last_image_preview, user_session_state]
        ).then(
            fn=None,
            inputs=[user_session_state],
            js="""
            function(session) {
                if (session && session.tokens !== undefined && window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'token-updated',
                        tokens: session.tokens
                    }, '*');
                }
            }
            """
        )
        
        # Item 생성 래퍼 함수 (UI 업데이트 포함)
        def generate_item_wrapper(item_description, item_art_style, item_mood, item_color_palette, item_line_style, 
                                  item_composition, item_additional_notes, item_reference_image,
                                  item_image_width=None, item_image_height=None, item_lock_aspect_ratio=False, 
                                  item_use_percentage=False, user_session=None, access_token=None):
            """Item 생성하고 UI 업데이트"""
            session = user_session or _default_user_session()
            
            # 세션이 인증되지 않았지만 토큰이 있으면 직접 인증 시도
            if not session.get("authenticated") and access_token and access_token.strip():
                try:
                    claims = validate_access_token(access_token.strip())
                    user_id = claims.get("sub")
                    if user_id:
                        tokens = ensure_user_token_balance(user_id)
                        session = {
                            "authenticated": True,
                            "user_id": user_id,
                            "tokens": tokens,
                            "access_token": access_token.strip(),
                        }
                except Exception:
                    pass
            
            if not session.get("authenticated"):
                return [
                    gr.update(visible=True),
                    gr.update(visible=False),
                    "Please sign in to generate items.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if session.get("tokens", 0) <= 0:
                return [
                    gr.update(visible=True),
                    gr.update(visible=False),
                    "You have no tokens remaining.",
                    gr.update(value=_format_token_text(0), visible=True),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if not item_description or not item_description.strip():
                return [
                    gr.update(visible=True),  # item_hero
                    gr.update(visible=False),  # item_output
                    "Please enter an item description.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]
            
            if item_image_width:
                img_path, status = generate_item_interface(
                    item_description, item_art_style, item_mood, item_color_palette, item_line_style, 
                    item_composition, item_additional_notes, item_reference_image,
                    item_image_width, item_image_height, item_lock_aspect_ratio, item_use_percentage
                )
            else:
                img_path, status = generate_item_interface(
                    item_description, item_art_style, item_mood, item_color_palette, item_line_style, 
                    item_composition, item_additional_notes, item_reference_image
                )
            
            token_update = _token_component_update_from_state(session)
            last_image_update = _last_image_component_update_from_state(session)

            if img_path:
                try:
                    remaining = consume_user_token(session["user_id"])
                    session["tokens"] = remaining
                    metadata = {
                        "description": item_description,
                        "art_style": item_art_style,
                    }
                    public_url = record_generated_image(
                        session["user_id"],
                        "item",
                        img_path,
                        metadata=metadata,
                    )
                    session["last_image_url"] = public_url
                    token_update = gr.update(value=_format_token_text(remaining), visible=True)
                    last_image_update = gr.update(value=public_url, visible=True)
                except Exception as logging_error:  # noqa: BLE001
                    print(f"[Item] Failed to record image: {logging_error}")

                return [
                    gr.update(visible=False),  # item_hero 숨기기
                    gr.update(value=img_path, visible=True),  # item_output 표시
                    status,
                    token_update,
                    last_image_update,
                    session,
                ]
            else:
                return [
                    gr.update(visible=True),  # item_hero 표시
                    gr.update(visible=False),  # item_output 숨기기
                    status,
                    token_update,
                    last_image_update,
                    session,
                ]
        
        # Item 생성 버튼 이벤트 핸들러
        generate_item_btn.click(
            fn=generate_item_wrapper,
            inputs=[item_description, item_art_style, item_mood, item_color_palette, item_line_style, item_composition, item_additional_notes, item_reference_image,
                    item_image_width, item_image_height, item_lock_aspect_ratio, item_use_percentage, user_session_state, token_input],
            outputs=[item_hero, item_output, item_status, token_display, last_image_preview, user_session_state]
        ).then(
            fn=None,
            inputs=[user_session_state],
            js="""
            function(session) {
                if (session && session.tokens !== undefined && window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'token-updated',
                        tokens: session.tokens
                    }, '*');
                }
            }
            """
        )
        
        # Sprites 생성 래퍼 함수 (UI 업데이트 포함)
        def generate_sprites_wrapper(sprite_character_description, actions_text, sprite_art_style, sprite_mood, 
                                     sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, 
                                     sprite_additional_notes, sprite_reference_image,
                                     sprite_image_width=None, sprite_image_height=None, sprite_lock_aspect_ratio=False, 
                                     sprite_use_percentage=False, user_session=None, access_token=None):
            """Sprites 생성하고 UI 업데이트"""
            session = user_session or _default_user_session()
            
            # 세션이 인증되지 않았지만 토큰이 있으면 직접 인증 시도
            if not session.get("authenticated") and access_token and access_token.strip():
                try:
                    claims = validate_access_token(access_token.strip())
                    user_id = claims.get("sub")
                    if user_id:
                        tokens = ensure_user_token_balance(user_id)
                        session = {
                            "authenticated": True,
                            "user_id": user_id,
                            "tokens": tokens,
                            "access_token": access_token.strip(),
                        }
                except Exception:
                    pass
            
            if not session.get("authenticated"):
                return [
                    gr.update(visible=True),
                    gr.update(value=[], visible=False),
                    "Please sign in to generate sprites.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if session.get("tokens", 0) <= 0:
                return [
                    gr.update(visible=True),
                    gr.update(value=[], visible=False),
                    "You have no tokens remaining.",
                    gr.update(value=_format_token_text(0), visible=True),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if not sprite_character_description or not sprite_character_description.strip():
                return [
                    gr.update(visible=True),  # sprites_hero
                    gr.update(value=[], visible=False),  # sprites_gallery
                    "Please enter a character description.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]
            
            if not actions_text or not actions_text.strip():
                return [
                    gr.update(visible=True),  # sprites_hero
                    gr.update(value=[], visible=False),  # sprites_gallery
                    "Please enter actions separated by commas.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]
            
            if sprite_image_width:
                image_paths, status = generate_character_sprites_interface(
                    sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, 
                    sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes, 
                    sprite_reference_image, sprite_image_width, sprite_image_height, sprite_lock_aspect_ratio, 
                    sprite_use_percentage
                )
            else:
                image_paths, status = generate_character_sprites_interface(
                    sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, 
                    sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes, 
                    sprite_reference_image
                )
            
            token_update = _token_component_update_from_state(session)
            last_image_update = _last_image_component_update_from_state(session)

            if image_paths and len(image_paths) > 0:
                try:
                    remaining = consume_user_token(session["user_id"])
                    session["tokens"] = remaining
                    metadata = {
                        "description": sprite_character_description,
                        "actions": actions_text,
                    }
                    preview_path = image_paths[-1] if image_paths else None
                    if preview_path:
                        public_url = record_generated_image(
                            session["user_id"],
                            "sprite_sheet",
                            preview_path,
                            metadata=metadata,
                        )
                        session["last_image_url"] = public_url
                        last_image_update = gr.update(value=public_url, visible=True)
                    token_update = gr.update(value=_format_token_text(remaining), visible=True)
                except Exception as logging_error:  # noqa: BLE001
                    print(f"[Sprites] Failed to record image: {logging_error}")

                return [
                    gr.update(visible=False),  # sprites_hero 숨기기
                    gr.update(value=image_paths, visible=True),  # sprites_gallery 표시
                    status,
                    token_update,
                    last_image_update,
                    session,
                ]
            else:
                return [
                    gr.update(visible=True),  # sprites_hero 표시
                    gr.update(value=[], visible=False),  # sprites_gallery 숨기기
                    status,
                    token_update,
                    last_image_update,
                    session,
                ]
        
        # Sprites 생성 버튼 이벤트 핸들러
        generate_sprites_btn.click(
            fn=generate_sprites_wrapper,
            inputs=[sprite_character_description, actions_text, sprite_art_style, sprite_mood, sprite_color_palette, sprite_character_style, sprite_line_style, sprite_composition, sprite_additional_notes, sprite_reference_image,
                    sprite_image_width, sprite_image_height, sprite_lock_aspect_ratio, sprite_use_percentage, user_session_state, token_input],
            outputs=[sprites_hero, sprites_gallery, sprites_status, token_display, last_image_preview, user_session_state]
        ).then(
            fn=None,
            inputs=[user_session_state],
            js="""
            function(session) {
                if (session && session.tokens !== undefined && window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'token-updated',
                        tokens: session.tokens
                    }, '*');
                }
            }
            """
        )

        def generate_background_wrapper(background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes,
                                        bg_image_width=None, bg_image_height=None, bg_lock_aspect_ratio=False, bg_use_percentage=False, user_session=None, access_token=None):
            session = user_session or _default_user_session()
            
            # 세션이 인증되지 않았지만 토큰이 있으면 직접 인증 시도
            if not session.get("authenticated") and access_token and access_token.strip():
                try:
                    claims = validate_access_token(access_token.strip())
                    user_id = claims.get("sub")
                    if user_id:
                        tokens = ensure_user_token_balance(user_id)
                        session = {
                            "authenticated": True,
                            "user_id": user_id,
                            "tokens": tokens,
                            "access_token": access_token.strip(),
                        }
                except Exception:
                    pass
            
            if not session.get("authenticated"):
                return [
                    gr.update(visible=False),
                    "Please sign in to generate backgrounds.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if session.get("tokens", 0) <= 0:
                return [
                    gr.update(visible=False),
                    "You have no tokens remaining.",
                    gr.update(value=_format_token_text(0), visible=True),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if bg_image_width:
                img_path, status = generate_background_interface(
                    background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes,
                    bg_image_width, bg_image_height, bg_lock_aspect_ratio, bg_use_percentage
                )
            else:
                img_path, status = generate_background_interface(
                    background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes
                )

            token_update = _token_component_update_from_state(session)
            last_image_update = _last_image_component_update_from_state(session)

            if img_path:
                try:
                    remaining = consume_user_token(session["user_id"])
                    session["tokens"] = remaining
                    metadata = {
                        "description": background_description,
                        "orientation": orientation,
                    }
                    public_url = record_generated_image(
                        session["user_id"],
                        "background",
                        img_path,
                        metadata=metadata,
                    )
                    session["last_image_url"] = public_url
                    token_update = gr.update(value=_format_token_text(remaining), visible=True)
                    last_image_update = gr.update(value=public_url, visible=True)
                except Exception as logging_error:  # noqa: BLE001
                    print(f"[Background] Failed to record image: {logging_error}")

                image_update = gr.update(value=img_path, visible=True)
            else:
                image_update = gr.update(visible=False)

            return [
                image_update,
                status,
                token_update,
                last_image_update,
                session,
            ]

        generate_background_btn.click(
            fn=generate_background_wrapper,
            inputs=[background_description, orientation, bg_art_style, bg_mood, bg_color_palette, bg_line_style, bg_composition, bg_additional_notes,
                    bg_image_width, bg_image_height, bg_lock_aspect_ratio, bg_use_percentage, user_session_state, token_input],
            outputs=[background_output, background_status, token_display, last_image_preview, user_session_state]
        ).then(
            fn=None,
            inputs=[user_session_state],
            js="""
            function(session) {
                if (session && session.tokens !== undefined && window.parent && window.parent !== window) {
                    window.parent.postMessage({
                        type: 'token-updated',
                        tokens: session.tokens
                    }, '*');
                }
            }
            """
        )
        
        # Sprite Animation 이벤트 핸들러
        def generate_animation_wrapper(reference_image, action_type, user_session, access_token=None):
            session = user_session or _default_user_session()
            
            # 세션이 인증되지 않았지만 토큰이 있으면 직접 인증 시도
            if not session.get("authenticated") and access_token and access_token.strip():
                try:
                    claims = validate_access_token(access_token.strip())
                    user_id = claims.get("sub")
                    if user_id:
                        tokens = ensure_user_token_balance(user_id)
                        session = {
                            "authenticated": True,
                            "user_id": user_id,
                            "tokens": tokens,
                            "access_token": access_token.strip(),
                        }
                except Exception:
                    pass
            
            if not session.get("authenticated"):
                return [
                    gr.update(value=[], visible=False),
                    "Please sign in to generate animations.",
                    _token_component_update_from_state(session),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            if session.get("tokens", 0) <= 0:
                return [
                    gr.update(value=[], visible=False),
                    "You have no tokens remaining.",
                    gr.update(value=_format_token_text(0), visible=True),
                    _last_image_component_update_from_state(session),
                    session,
                ]

            image_paths, status = generate_universal_animation(reference_image, action_type)
            token_update = _token_component_update_from_state(session)
            last_image_update = _last_image_component_update_from_state(session)

            if image_paths:
                try:
                    remaining = consume_user_token(session["user_id"])
                    session["tokens"] = remaining
                    preview_path = image_paths[-1]
                    public_url = record_generated_image(
                        session["user_id"],
                        f"sprite_animation_{action_type}".lower(),
                        preview_path,
                        metadata={"action_type": action_type},
                    )
                    session["last_image_url"] = public_url
                    token_update = gr.update(value=_format_token_text(remaining), visible=True)
                    last_image_update = gr.update(value=public_url, visible=True)
                except Exception as logging_error:  # noqa: BLE001
                    print(f"[Animation] Failed to record image: {logging_error}")

                gallery_update = gr.update(value=image_paths, visible=True)
            else:
                gallery_update = gr.update(value=[], visible=False)

            return [
                gallery_update,
                status,
                token_update,
                last_image_update,
                session,
            ]

        generate_sprite_btn.click(
            fn=generate_animation_wrapper,
            inputs=[enhanced_sprite_reference_image, action_type_dropdown, user_session_state, token_input],
            outputs=[sprite_gallery, sprite_status, token_display, last_image_preview, user_session_state]
        )
        
        # Download ZIP button handler
        def download_zip_wrapper(image_paths, action_type):
            normalized_type = (action_type or "").strip().lower() or "animation"
            zip_path, status = create_sprite_animation_zip(image_paths, normalized_type)
            if zip_path:
                return gr.update(value=zip_path, visible=True), status
            else:
                return gr.update(visible=False), status
        
        download_zip_btn.click(
            fn=download_zip_wrapper,
            inputs=[sprite_gallery, action_type_dropdown],
            outputs=[sprite_zip_download, sprite_zip_status]
        )
        
        # Action type 변경 시 정보 업데이트
        action_type_dropdown.change(
            fn=update_animation_info,
            inputs=[action_type_dropdown],
            outputs=[animation_info, frame_info]
        )

        # 로그인/회원가입 버튼 이벤트 제거 (Next.js에서 처리)
        # signup_button.click(...) 제거
        # login_button.click(...) 제거

        logout_button.click(
            fn=handle_sign_out,
            inputs=[user_session_state],
            outputs=[auth_status, token_display, last_image_preview, user_meta_row, user_session_state]
        )
        
        # 자동 로그인 처리 (페이지 로드 시 최우선 실행)
        demo.load(
            fn=handle_auto_login_from_token,
            inputs=[token_input],
            outputs=[auth_status, token_display, last_image_preview, user_meta_row, user_session_state, token_input],
            js="""
            function() {
                // 여러 방법으로 토큰 읽기 시도
                let token = '';
                
                // 방법 1: URLSearchParams 사용
                try {
                    const urlParams = new URLSearchParams(window.location.search);
                    token = urlParams.get('token') || '';
                } catch (e) {
                    console.error('[Auto-login] Error reading URL params:', e);
                }
                
                // 방법 2: 전체 URL에서 직접 추출 (fallback)
                if (!token) {
                    try {
                        const url = window.location.href;
                        const match = url.match(/[?&]token=([^&]+)/);
                        if (match) {
                            token = decodeURIComponent(match[1]);
                        }
                    } catch (e) {
                        console.error('[Auto-login] Error extracting from URL:', e);
                    }
                }
                
                console.log('[Auto-login] Token from URL:', token ? 'Found (' + token.substring(0, 20) + '...)' : 'Not found');
                return token;  // 배열이 아닌 단일 값 반환
            }
            """
        )

        demo.load(
            fn=_refresh_all_config_dropdowns,
            outputs=[
                load_config_dropdown,
                delete_config_dropdown,
                char_config_dropdown,
                sprite_config_dropdown,
                bg_config_dropdown,
                item_config_dropdown,
            ],
        )

    return demo

if __name__ == "__main__":
    demo = create_game_asset_interface()
    demo.launch(
        share=True, 
        server_name="0.0.0.0", 
        server_port=7861
    )

