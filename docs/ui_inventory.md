# UI Inventory – Gemini UI System

Latest snapshot of the shared UI system that we will now apply to **all tabs except Settings**. The source of truth is the `🎨 Character Creation` tab.

---

## 1. Layout Building Blocks

| Component | Description | Location |
|-----------|-------------|----------|
| `gr.Column(elem_classes=["gemini-center-container"])` | Hero area containing the “What do you want to create today?” message and the main output (image / gallery). Ensures the hero stays vertically centered with generous padding. | Character Creation (lines ~1930–1990) |
| `.gemini-welcome-text` | Fun gaming font (`Press Start 2P`), enlarged to 2.2rem, used for hero questions / titles. | CSS block in `backend/game_asset_app.py` |
| `.gemini-search-container` + `.gemini-search-box` | Fixed bottom search/input area that hosts upload + text input + primary action button. | Character Creation search row (`backend/game_asset_app.py`) |
| `.reference-plus-upload` | Styling hook that turns a standard `gr.File` component into a circular `+` button without losing Gradio’s native upload logic. | CSS block; used for reference uploads |
| Advanced Settings Accordion | `gr.Accordion("⚙️ Advanced Settings", ...)` with grouped sections for Style preferences, Image Size, Load Settings, etc. | Character Creation after hero area |
| Status + hidden prompts | `gr.Textbox` components kept hidden to show status strings or generated prompts when needed. | Character Creation bottom |

---

## 2. Interactive Controls

### 2.1 Plus-Style File Uploader
- Use `create_reference_upload(..., elem_classes=["reference-plus-upload"], show_label=False)` so the underlying `gr.File` remains intact.
- CSS hides the default label and replaces it with a circular button showing “+”.
- Applies to:
  - Character Creation reference image
  - Item Generation style reference
  - Character Sprites reference
  - Sprite Animation reference
  - Background reference

### 2.2 Search Row Inputs
- Consists of `[plus uploader] + [text input(s)] + [primary action button]`.
- Each text input uses `.gemini-search-input`.
- Primary action uses `.gemini-generate-btn` for consistent gradients and hover states.

### 2.3 Advanced Settings Accordion
- Sections included:
  - **Style Preferences** (two-column dropdown grid)
  - **Additional Style Notes** (`gr.Textbox`)
  - **Image Size Adjustment** (shared helper `create_image_size_controls()`)
  - **Load Settings** (dropdown + small button)
- Additional tab-specific controls (e.g., Actions text, Orientation radio) can be placed either in the accordion or directly below the search row, depending on frequency of use.

---

## 3. Output Displays

| Tab | Output Component | Placement |
|-----|------------------|-----------|
| Item Generation | `item_output = gr.Image(...)` | Inside `gemini-center-container` |
| Character Creation | `character_output = gr.Image(...)` | Already in hero area |
| Character Sprites | `sprites_gallery = gr.Gallery(...)` | Should be moved into hero area |
| Sprite Animation | `sprite_gallery` / `sprite_status` (depending on action) | Use hero area for preview image(s) and textual status |
| Background | `background_output = gr.Image(...)` | Move into hero area |

---

## 4. Implementation Checklist

1. **Inventory doc (this file).**
2. **Helper updates** – extend `create_reference_upload` to accept extra options (e.g., `elem_classes`, `show_label=False`, `elem_id`, `type="filepath"`).
3. **Apply Character Creation layout** to:
   - ✅ 🎒 Item Generation – hero + accordion + bottom search row.
   - ✅ 🏃 Character Sprites – same structure plus actions input.
   - ✅ 🎮 Sprite Animation – hero preview, plus uploader, action dropdown.
   - ✅ 🌄 Background – hero preview, accordion for orientation/style, bottom search row.
4. **Verify** `python3 -m py_compile backend/game_asset_app.py`.
5. **Document final structure** (see section 6).

---

## 5. Notes
- All tabs should eventually share the same `gemini-search-container` + hero layout so that the app feels cohesive.
- Keep Settings tab untouched; it stays as the administrative view.

---

## 6. Tab Quick Reference

| Tab | Hero Output | Advanced Settings | Search Row Inputs | Extras |
|-----|-------------|-------------------|-------------------|--------|
| 🎒 Item Generation | `item_output` image | Style prefs, notes, image size, load settings | `[style reference +][item_description][Generate Item]` | `item_status`, `item_prompt_display` |
| 🎨 Character Creation | `character_output` image | Style prefs, image size, load settings, Pixel toggle | `[character reference +][character_description][Generate Character]` | Hidden status + prompt |
| 🏃 Character Sprites | `sprites_gallery` | Style prefs, notes, image size, load settings | `[sprite reference +][character_description][actions_text][Generate]` | Hidden status + prompt |
| 🎮 Sprite Animation | `sprite_gallery` | Animation guidance + info text | `[animation reference +][action dropdown][Generate Animation]` | ZIP download + status |
| 🌄 Background | `background_output` | Orientation, style prefs, notes, image size, load settings | `[background description][Generate Background]` | Hidden status + prompt |

