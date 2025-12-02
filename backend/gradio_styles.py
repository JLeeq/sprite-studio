"""CSS 스타일 정의"""

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

    #login-overlay {
        position: fixed;
        inset: 0;
        background: rgba(6, 9, 23, 0.95);
        z-index: 999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 2rem;
        text-align: center;
        backdrop-filter: blur(8px);
    }

    #login-overlay .gr-textbox,
    #login-overlay .gr-button {
        width: 320px;
        max-width: 100%;
    }

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
