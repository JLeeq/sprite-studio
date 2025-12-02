# UI Component Inventory
## 2D Game Asset Generator - Design System Documentation

> **목적**: 디자인 시스템 문서화를 위한 UI 컴포넌트 인벤토리  
> **버전**: 1.0  
> **마지막 업데이트**: 2024

---

## 📋 목차

1. [컴포넌트 카테고리](#컴포넌트-카테고리)
2. [공통 컴포넌트](#공통-컴포넌트)
3. [제미나이 스타일 컴포넌트](#제미나이-스타일-컴포넌트)
4. [탭별 컴포넌트](#탭별-컴포넌트)
5. [재사용 가능성 분석](#재사용-가능성-분석)

---

## 컴포넌트 카테고리

### 1. 기본 UI 컴포넌트 (Base Components)
- **위치**: `backend/game_asset_app.py` (함수 정의)
- **용도**: 모든 탭에서 공통으로 사용되는 기본 컴포넌트

### 2. 제미나이 스타일 컴포넌트 (Gemini Style Components)
- **위치**: `backend/game_asset_app.py` (CSS + 컴포넌트)
- **용도**: 제미나이 스타일 UI를 구현하는 특수 컴포넌트

### 3. 탭별 전용 컴포넌트 (Tab-Specific Components)
- **위치**: 각 탭 내부
- **용도**: 특정 탭에서만 사용되는 컴포넌트

---

## 공통 컴포넌트

### ✅ 이미 구현된 공통 함수들

#### 1. `create_config_dropdown(initial_configs, label)`
- **타입**: Dropdown
- **용도**: 설정 불러오기 드롭다운
- **반환값**: `gr.Dropdown`
- **재사용**: ✅ 모든 탭에서 사용
- **위치**: Line 893-901

```python
def create_config_dropdown(initial_configs, label="Saved Settings Selection"):
    return gr.Dropdown(
        choices=initial_configs,
        value="None",
        label=label,
        interactive=True,
        allow_custom_value=True
    )
```

#### 2. `create_reference_upload(label, file_types)`
- **타입**: File Upload
- **용도**: 참조 이미지 업로드
- **반환값**: `gr.File`
- **재사용**: ✅ 모든 탭에서 사용
- **위치**: Line 903-905

```python
def create_reference_upload(label="Upload Reference", file_types=FILE_TYPES):
    return gr.File(label=label, file_types=file_types)
```

#### 3. `create_image_size_controls()`
- **타입**: Group (Number inputs + Checkbox)
- **용도**: 이미지 크기 조정 컨트롤
- **반환값**: `(image_width, image_height, lock_aspect_ratio, use_percentage)`
- **재사용**: ✅ 모든 탭에서 사용
- **위치**: Line 907-940

```python
def create_image_size_controls():
    # ... 구현
    return image_width, image_height, lock_aspect_ratio, use_percentage
```

---

## 제미나이 스타일 컴포넌트

### 현재 구현 상태

#### 1. 중앙 컨테이너 (Center Container)
- **CSS 클래스**: `.gemini-center-container`
- **구조**:
  - Welcome 텍스트 (`.gemini-welcome-text`)
  - 생성된 이미지 (`.gemini-image-container`)
- **위치**: Character Creation 탭 (Line 1859-1873)
- **재사용 가능**: ⚠️ 아직 함수화되지 않음

#### 2. 하단 검색창 (Search Bar)
- **CSS 클래스**: `.gemini-search-container`, `.gemini-search-box`
- **구조**:
  - + 버튼 (`.gemini-upload-btn`)
  - 검색 입력창 (`.gemini-search-input`)
- **위치**: Character Creation 탭 (Line 1938-1965)
- **재사용 가능**: ⚠️ 아직 함수화되지 않음

#### 3. Advanced Settings 모달
- **CSS 클래스**: `.gemini-modal-container`, `.gemini-modal-body`
- **구조**:
  - 모달 헤더
  - 모달 바디 (스크롤 가능)
  - 모달 푸터
- **위치**: Character Creation 탭 (Line 1890-1936)
- **재사용 가능**: ⚠️ 아직 함수화되지 않음

#### 4. Pixel Mode 토글
- **CSS 클래스**: `.gemini-pixel-mode-toggle`
- **타입**: Checkbox
- **위치**: Character Creation 탭 (Line 1882-1888)
- **재사용 가능**: ⚠️ 아직 함수화되지 않음

---

## 탭별 컴포넌트

### 🎨 Character Creation 탭
**구조**:
```
Character Creation Tab
├── 중앙 컨테이너
│   ├── Welcome 텍스트
│   └── 생성된 이미지
├── Advanced Settings 버튼 (상단 좌측)
├── Pixel Mode 체크박스 (Advanced Settings 아래)
├── Advanced Settings 모달
│   ├── Style Preferences
│   ├── Image Size Adjustment
│   └── Load Settings
└── 하단 검색창
    ├── + 버튼
    └── 검색 입력창
```

**컴포넌트 목록**:
- `welcome_text` (Markdown)
- `character_output` (Image)
- `advanced_settings_btn` (Button)
- `character_mode` (Checkbox)
- `advanced_settings_modal` (Column)
- `upload_btn` (Button)
- `character_description` (Textbox)

### 🎒 Item Generation 탭
**현재 상태**: 기존 스타일 (2-column 레이아웃)
**변경 필요**: Character Creation과 동일한 UI 적용

### 🏃 Character Sprites 탭
**현재 상태**: 기존 스타일 (2-column 레이아웃)
**변경 필요**: Character Creation과 동일한 UI 적용

### 🌄 Background 탭
**현재 상태**: 기존 스타일 (2-column 레이아웃)
**변경 필요**: Character Creation과 동일한 UI 적용

### 🎮 Sprite Animation 탭
**현재 상태**: 기존 스타일
**변경 필요**: Character Creation과 동일한 UI 적용 (선택사항)

---

## 재사용 가능성 분석

### ✅ 공통 함수로 만들 수 있는 컴포넌트

#### 1. `create_gemini_center_container(welcome_text, output_image)`
```python
def create_gemini_center_container(welcome_text_content, output_image_id):
    """
    제미나이 스타일 중앙 컨테이너 생성
    
    Args:
        welcome_text_content: Welcome 텍스트 내용
        output_image_id: 출력 이미지 컴포넌트 ID
    
    Returns:
        (welcome_text, output_image): Gradio 컴포넌트 튜플
    """
    with gr.Column(elem_classes=["gemini-center-container"]):
        welcome_text = gr.Markdown(
            welcome_text_content,
            elem_classes=["gemini-welcome-text"],
            visible=True
        )
        output_image = gr.Image(
            label="",
            show_label=False,
            visible=False,
            elem_classes=["gemini-image-container"],
            elem_id=output_image_id
        )
    return welcome_text, output_image
```

#### 2. `create_gemini_search_bar(placeholder, upload_btn_id, input_id)`
```python
def create_gemini_search_bar(placeholder, upload_btn_id, input_id):
    """
    제미나이 스타일 하단 검색창 생성
    
    Args:
        placeholder: 검색창 placeholder 텍스트
        upload_btn_id: 업로드 버튼 ID
        input_id: 입력창 ID
    
    Returns:
        (upload_btn, search_input, hidden_upload): Gradio 컴포넌트 튜플
    """
    with gr.Row(elem_classes=["gemini-search-container"]):
        with gr.Column():
            with gr.Row(elem_classes=["gemini-search-box"]):
                upload_btn = gr.Button("+", ...)
                search_input = gr.Textbox(placeholder=placeholder, ...)
                hidden_upload = gr.File(...)
    return upload_btn, search_input, hidden_upload
```

#### 3. `create_advanced_settings_modal(modal_id, initial_configs, style_options)`
```python
def create_advanced_settings_modal(modal_id, initial_configs, style_options):
    """
    Advanced Settings 모달 생성
    
    Args:
        modal_id: 모달 고유 ID
        initial_configs: 설정 목록
        style_options: 스타일 옵션 딕셔너리
    
    Returns:
        (modal, btn, close_btn1, close_btn2, ...): 모달 및 관련 컴포넌트들
    """
    # 모달 구조 생성
    # ...
    return modal, btn, close_btn1, close_btn2, style_components...
```

#### 4. `create_pixel_mode_toggle(toggle_id)`
```python
def create_pixel_mode_toggle(toggle_id):
    """
    Pixel Mode 체크박스 생성
    
    Args:
        toggle_id: 체크박스 고유 ID
    
    Returns:
        pixel_mode_checkbox: Gradio Checkbox 컴포넌트
    """
    with gr.Row(elem_classes=["gemini-pixel-mode-toggle"]):
        pixel_mode = gr.Checkbox(
            label="Pixel Mode",
            value=False,
            elem_id=toggle_id
        )
    return pixel_mode
```

### 📊 재사용 가능성 매트릭스

| 컴포넌트 | 현재 상태 | 함수화 가능 | 우선순위 |
|---------|----------|------------|---------|
| 중앙 컨테이너 | ⚠️ 인라인 | ✅ 가능 | 높음 |
| 하단 검색창 | ⚠️ 인라인 | ✅ 가능 | 높음 |
| Advanced Settings 모달 | ⚠️ 인라인 | ✅ 가능 | 높음 |
| Pixel Mode 토글 | ⚠️ 인라인 | ✅ 가능 | 중간 |
| Advanced Settings 버튼 | ⚠️ 인라인 | ✅ 가능 | 중간 |

---

## 구현 계획

### Phase 1: 공통 함수 생성
1. `create_gemini_center_container()` 구현
2. `create_gemini_search_bar()` 구현
3. `create_advanced_settings_modal()` 구현
4. `create_pixel_mode_toggle()` 구현
5. `create_advanced_settings_button()` 구현

### Phase 2: Character Creation 탭 리팩토링
- 기존 인라인 코드를 공통 함수로 교체

### Phase 3: 다른 탭들 적용
- Item Generation 탭
- Character Sprites 탭
- Background 탭
- Sprite Animation 탭 (선택사항)

---

## 결론

### ✅ 재사용 가능: **예**

**이유**:
1. 이미 공통 함수 패턴이 존재 (`create_config_dropdown`, `create_reference_upload` 등)
2. 제미나이 스타일 컴포넌트들이 명확한 구조를 가짐
3. 모든 탭에서 동일한 UI 패턴 사용 가능
4. 함수화하면 코드 중복 제거 및 유지보수 용이

**예상 효과**:
- 코드 라인 수: ~500줄 감소
- 유지보수성: 크게 향상
- 일관성: 모든 탭에서 동일한 UI 보장
- 확장성: 새로운 탭 추가 시 쉽게 적용 가능

**권장 사항**:
1. 공통 함수들을 먼저 구현
2. Character Creation 탭을 리팩토링하여 검증
3. 다른 탭들에 순차적으로 적용

---

## 다음 단계

1. ✅ Pixel Mode 버튼 위치 수정 (완료)
2. ⏳ 공통 함수 구현
3. ⏳ Character Creation 탭 리팩토링
4. ⏳ 다른 탭들 적용


