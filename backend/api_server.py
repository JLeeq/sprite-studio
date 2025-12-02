import os
import tempfile
from typing import Optional, Dict, Any

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    Depends,
    Header,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware

from .supabase_client import (
    validate_access_token,
    ensure_user_token_balance,
    get_user_token_balance,
    consume_user_token,
    record_generated_image,
    get_last_generated_image_url,
    sign_up_user,
    sign_in_user,
    sign_out_user,
)
from .game_asset_app import (
    generate_character_interface,
    generate_character_sprites_interface,
    generate_background_interface,
    generate_item_interface,
    generate_universal_animation,
    build_user_preferences,
)
from .pixel_character_generator import generate_pixel_character_interface


def create_app() -> FastAPI:
    app = FastAPI(title="Sprite Studio API")

    allowed_origins = os.getenv("API_ALLOWED_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in allowed_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _optional(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value or value.lower() == "none":
            return None
        return value

    async def _save_upload(upload: Optional[UploadFile]) -> Optional[str]:
        if upload is None:
            return None
        suffix = os.path.splitext(upload.filename or "")[1] or ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await upload.read()
            tmp.write(contents)
            return tmp.name

    def _cleanup_temp(*paths: Optional[str]) -> None:
        for path in paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _tokens_or_402(user_session: Dict[str, Any]) -> None:
        if user_session.get("tokens", 0) <= 0:
            raise HTTPException(status_code=402, detail="No tokens remaining.")

    def _auth_dependency(authorization: str = Header(...)) -> Dict[str, Any]:
        if not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization header.")
        raw_token = authorization.split(" ", 1)[1].strip()
        claims = validate_access_token(raw_token)
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token claims.")
        tokens = ensure_user_token_balance(user_id)
        return {
            "user_id": user_id,
            "tokens": tokens,
            "access_token": raw_token,
        }

    @app.post("/auth/signup")
    async def api_sign_up(email: str = Form(...), password: str = Form(...)):
        try:
            response = sign_up_user(email, password)
            return {"message": "Check your inbox to verify the account.", "data": response}
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/auth/login")
    async def api_login(email: str = Form(...), password: str = Form(...)):
        try:
            response = sign_in_user(email, password)
            session = getattr(response, "session", None)
            user = getattr(response, "user", None)
            if not session or not user:
                raise HTTPException(status_code=400, detail="Invalid Supabase response.")
            return {
                "message": "Signed in successfully.",
                "session": {
                    "access_token": getattr(session, "access_token", None),
                    "refresh_token": getattr(session, "refresh_token", None),
                    "expires_at": getattr(session, "expires_at", None),
                },
                "user": {"id": getattr(user, "id", None), "email": getattr(user, "email", None)},
            }
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/auth/logout")
    async def api_logout():
        try:
            sign_out_user()
        except Exception:
            pass
        return {"message": "Signed out."}

    @app.get("/profile")
    async def profile(user=Depends(_auth_dependency)):
        last_image = get_last_generated_image_url(user["user_id"])
        tokens = get_user_token_balance(user["user_id"])
        return {"user_id": user["user_id"], "tokens": tokens, "last_image_url": last_image}

    @app.post("/generate/character")
    async def generate_character(
        character_description: str = Form(...),
        art_style: str = Form("None"),
        mood: str = Form("None"),
        color_palette: str = Form("None"),
        character_style: str = Form("None"),
        line_style: str = Form("None"),
        composition: str = Form("None"),
        additional_notes: str = Form(""),
        character_reference_image: Optional[UploadFile] = File(None),
        item_reference_image: Optional[UploadFile] = File(None),
        image_width: Optional[str] = Form(None),
        image_height: Optional[str] = Form(None),
        lock_aspect_ratio: bool = Form(False),
        use_percentage: bool = Form(False),
        pixel_mode: bool = Form(False),
        user=Depends(_auth_dependency),
    ):
        _tokens_or_402(user)
        char_ref = await _save_upload(character_reference_image)
        item_ref = await _save_upload(item_reference_image)
        try:
            if pixel_mode:
                status, img_path = generate_pixel_character_interface(
                    character_description,
                    character_reference_image=char_ref,
                    item_reference_image=item_ref,
                )
            else:
                width = int(image_width) if image_width else None
                height = int(image_height) if image_height else None
                img_path, status = generate_character_interface(
                    character_description,
                    _optional(art_style),
                    _optional(mood),
                    _optional(color_palette),
                    _optional(character_style),
                    _optional(line_style),
                    _optional(composition),
                    additional_notes,
                    char_ref,
                    item_ref,
                    width,
                    height,
                    lock_aspect_ratio,
                    use_percentage,
                )
            if not img_path:
                raise HTTPException(status_code=400, detail=status)

            remaining = consume_user_token(user["user_id"])
            metadata = {
                "description": character_description,
                "art_style": art_style,
                "pixel_mode": pixel_mode,
            }
            public_url = record_generated_image(
                user["user_id"],
                "character_pixel" if pixel_mode else "character",
                img_path,
                metadata=metadata,
            )
            return {
                "message": status,
                "image_url": public_url,
                "tokens": remaining,
                "last_image_url": public_url,
            }
        finally:
            _cleanup_temp(char_ref, item_ref)

    @app.post("/generate/item")
    async def generate_item(
        item_description: str = Form(...),
        art_style: str = Form("None"),
        mood: str = Form("None"),
        color_palette: str = Form("None"),
        line_style: str = Form("None"),
        composition: str = Form("None"),
        additional_notes: str = Form(""),
        reference_image: Optional[UploadFile] = File(None),
        image_width: Optional[str] = Form(None),
        image_height: Optional[str] = Form(None),
        lock_aspect_ratio: bool = Form(False),
        use_percentage: bool = Form(False),
        user=Depends(_auth_dependency),
    ):
        _tokens_or_402(user)
        ref_path = await _save_upload(reference_image)
        try:
            width = int(image_width) if image_width else None
            height = int(image_height) if image_height else None
            img_path, status = generate_item_interface(
                item_description,
                _optional(art_style),
                _optional(mood),
                _optional(color_palette),
                _optional(line_style),
                _optional(composition),
                additional_notes,
                ref_path,
                width,
                height,
                lock_aspect_ratio,
                use_percentage,
            )
            if not img_path:
                raise HTTPException(status_code=400, detail=status)

            remaining = consume_user_token(user["user_id"])
            metadata = {
                "description": item_description,
                "art_style": art_style,
            }
            public_url = record_generated_image(
                user["user_id"],
                "item",
                img_path,
                metadata=metadata,
            )
            return {
                "message": status,
                "image_url": public_url,
                "tokens": remaining,
                "last_image_url": public_url,
            }
        finally:
            _cleanup_temp(ref_path)

    @app.post("/generate/sprites")
    async def generate_sprites(
        character_description: str = Form(...),
        actions_text: str = Form(...),
        art_style: str = Form("None"),
        mood: str = Form("None"),
        color_palette: str = Form("None"),
        character_style: str = Form("None"),
        line_style: str = Form("None"),
        composition: str = Form("None"),
        additional_notes: str = Form(""),
        reference_image: Optional[UploadFile] = File(None),
        image_width: Optional[str] = Form(None),
        image_height: Optional[str] = Form(None),
        lock_aspect_ratio: bool = Form(False),
        use_percentage: bool = Form(False),
        user=Depends(_auth_dependency),
    ):
        _tokens_or_402(user)
        ref_path = await _save_upload(reference_image)
        try:
            width = int(image_width) if image_width else None
            height = int(image_height) if image_height else None
            image_paths, status = generate_character_sprites_interface(
                character_description,
                actions_text,
                _optional(art_style),
                _optional(mood),
                _optional(color_palette),
                _optional(character_style),
                _optional(line_style),
                _optional(composition),
                additional_notes,
                ref_path,
                width,
                height,
                lock_aspect_ratio,
                use_percentage,
            )
            if not image_paths:
                raise HTTPException(status_code=400, detail=status)

            remaining = consume_user_token(user["user_id"])
            preview_path = image_paths[-1]
            metadata = {
                "description": character_description,
                "actions": actions_text,
            }
            public_url = record_generated_image(
                user["user_id"],
                "sprite_sheet",
                preview_path,
                metadata=metadata,
            )
            return {
                "message": status,
                "image_urls": image_paths,
                "preview_url": public_url,
                "tokens": remaining,
                "last_image_url": public_url,
            }
        finally:
            _cleanup_temp(ref_path)

    @app.post("/generate/background")
    async def generate_background(
        background_description: str = Form(...),
        orientation: str = Form("landscape"),
        art_style: str = Form("None"),
        mood: str = Form("None"),
        color_palette: str = Form("None"),
        line_style: str = Form("None"),
        composition: str = Form("None"),
        additional_notes: str = Form(""),
        image_width: Optional[str] = Form(None),
        image_height: Optional[str] = Form(None),
        lock_aspect_ratio: bool = Form(False),
        use_percentage: bool = Form(False),
        user=Depends(_auth_dependency),
    ):
        _tokens_or_402(user)
        width = int(image_width) if image_width else None
        height = int(image_height) if image_height else None
        img_path, status = generate_background_interface(
            background_description,
            orientation,
            _optional(art_style),
            _optional(mood),
            _optional(color_palette),
            _optional(line_style),
            _optional(composition),
            additional_notes,
            width,
            height,
            lock_aspect_ratio,
            use_percentage,
        )
        if not img_path:
            raise HTTPException(status_code=400, detail=status)

        remaining = consume_user_token(user["user_id"])
        metadata = {
            "description": background_description,
            "orientation": orientation,
        }
        public_url = record_generated_image(
            user["user_id"],
            "background",
            img_path,
            metadata=metadata,
        )
        return {
            "message": status,
            "image_url": public_url,
            "tokens": remaining,
            "last_image_url": public_url,
        }

    @app.post("/generate/animation")
    async def generate_animation(
        reference_image: UploadFile = File(...),
        action_type: str = Form("attack"),
        user=Depends(_auth_dependency),
    ):
        _tokens_or_402(user)
        ref_path = await _save_upload(reference_image)
        try:
            image_paths, status = generate_universal_animation(ref_path, action_type)
            if not image_paths:
                raise HTTPException(status_code=400, detail=status)

            remaining = consume_user_token(user["user_id"])
            preview_path = image_paths[-1]
            metadata = {"action_type": action_type}
            public_url = record_generated_image(
                user["user_id"],
                f"animation_{action_type}",
                preview_path,
                metadata=metadata,
            )
            return {
                "message": status,
                "image_urls": image_paths,
                "preview_url": public_url,
                "tokens": remaining,
                "last_image_url": public_url,
            }
        finally:
            _cleanup_temp(ref_path)

    return app


app = create_app()

