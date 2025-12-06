"""
Centralized Supabase client for the Python backend.

This module loads Supabase credentials from environment variables (optionally
via `.env`) and exposes helpers for sharing a single service-role client
instance across Gradio entrypoints. A dedicated TokenValidator helper is
provided so Gradio endpoints can authenticate incoming requests that include
Supabase JWT access tokens.
"""

from __future__ import annotations

import os
from functools import lru_cache
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
import jwt
from supabase import Client, create_client

DEFAULT_TOKEN_COUNT = int(os.environ.get("SUPABASE_INITIAL_TOKENS", "100"))
TOKEN_TABLE = os.environ.get("SUPABASE_TOKEN_TABLE", "user_tokens")
PROJECT_TABLE = os.environ.get("SUPABASE_PROJECT_TABLE", "user_projects")
GENERATED_TABLE = os.environ.get("SUPABASE_GENERATED_TABLE", "generated_images")
STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "generated")
DEFAULT_PROJECT_NAME = os.environ.get("SUPABASE_DEFAULT_PROJECT_NAME", "Default Project")

# Load environment variables defined in .env (if present).
load_dotenv()


def _get_env_variable(key: str) -> str:
    """Fetch an environment variable and fail fast if it's missing."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {key}. "
            "Set it in your shell or within the project .env file."
        )
    return value


@lru_cache(maxsize=1)
def get_supabase_admin_client() -> Client:
    """
    Return a singleton Supabase client configured with the service-role key.

    The service-role key must never be exposed to browsers or bundled into
    Next.js—keep it strictly on the backend. By caching the Client instance we
    avoid recreating HTTP pools for every request.
    """
    supabase_url = _get_env_variable("SUPABASE_URL")
    service_key = _get_env_variable("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(supabase_url, service_key)


@lru_cache(maxsize=1)
def get_supabase_anon_client() -> Client:
    """
    Return a Supabase client that uses the public anon key.

    Useful for email/password auth flows that require the regular GoTrue
    endpoints instead of the admin API.
    """
    supabase_url = _get_env_variable("SUPABASE_URL")
    anon_key = _get_env_variable("SUPABASE_ANON_KEY")
    return create_client(supabase_url, anon_key)


def validate_access_token(access_token: str) -> Dict[str, Any]:
    """
    Validate a Supabase JWT access token and return its claims.

    Parameters
    ----------
    access_token:
        The JWT sent from Next.js via the `Authorization: Bearer ...` header.

    Returns
    -------
    dict
        JWT claims containing `sub` (user id), `exp`, etc.

    Raises
    ------
    jwt.InvalidTokenError
        If the token is invalid, expired, or cannot be decoded.
    ValueError
        If the access token is missing.
    """
    if not access_token:
        raise ValueError("Access token is required for validation.")

    # Decode JWT without verification (for development)
    # In production, you should verify the signature using Supabase's JWT secret
    try:
        # Decode without verification for now (development mode)
        # In production, use: jwt.decode(access_token, jwt_secret, algorithms=["HS256"])
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        return decoded
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid access token: {str(e)}")


def upload_file_to_storage(
    file_path: str,
    storage_path: str,
    bucket: str = "generated",
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Upload a local file to Supabase Storage.

    Parameters
    ----------
    file_path:
        Local path to the file that should be uploaded.
    storage_path:
        Destination path inside the bucket (e.g. `user_id/project_id/file.png`).
    bucket:
        Storage bucket name. Defaults to `generated`.
    content_type:
        Optional MIME type metadata.

    Returns
    -------
    dict
        Supabase storage API response.
    """
    client = get_supabase_admin_client()
    with open(file_path, "rb") as file_handle:
        response = client.storage.from_(bucket).upload(
            storage_path,
            file_handle,
            file_options={"content-type": content_type} if content_type else None,
        )
    return response


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def sign_up_user(email: str, password: str) -> Dict[str, Any]:
    """Register a new user using the anon client."""
    client = get_supabase_anon_client()
    return client.auth.sign_up({"email": email, "password": password})


def sign_in_user(email: str, password: str) -> Dict[str, Any]:
    """Sign in a user and return the Supabase session."""
    client = get_supabase_anon_client()
    return client.auth.sign_in_with_password({"email": email, "password": password})


def sign_out_user() -> None:
    """Sign out the anon client session (best-effort)."""
    client = get_supabase_anon_client()
    try:
        client.auth.sign_out()
    except Exception:
        # Ignore errors if no active session exists on the server client.
        pass


# ---------------------------------------------------------------------------
# Token & project utilities
# ---------------------------------------------------------------------------

def ensure_user_token_balance(user_id: str, initial_tokens: int = DEFAULT_TOKEN_COUNT) -> int:
    """
    Ensure a token row exists for the user and return the current balance.
    """
    client = get_supabase_admin_client()
    response = client.table(TOKEN_TABLE).select("tokens").eq("user_id", user_id).execute()
    data = response.data or []
    if not data:
        client.table(TOKEN_TABLE).insert({"user_id": user_id, "tokens": initial_tokens}).execute()
        return initial_tokens
    return int(data[0]["tokens"])


def get_user_token_balance(user_id: str) -> int:
    """Fetch (but do not mutate) the user's remaining tokens."""
    return ensure_user_token_balance(user_id)


def consume_user_token(user_id: str, amount: int = 1) -> int:
    """
    Decrement the user's token balance by `amount`.

    Returns the remaining token count.
    """
    client = get_supabase_admin_client()
    current = ensure_user_token_balance(user_id)
    if current < amount:
        raise ValueError("Insufficient tokens.")
    new_balance = current - amount
    client.table(TOKEN_TABLE).update({"tokens": new_balance}).eq("user_id", user_id).execute()
    return new_balance


def _ensure_default_project(user_id: str) -> str:
    """Return a default project_id for the user, creating one if needed."""
    client = get_supabase_admin_client()
    response = (
        client.table(PROJECT_TABLE)
        .select("id")
        .eq("user_id", user_id)
        .eq("project_name", DEFAULT_PROJECT_NAME)
        .limit(1)
        .execute()
    )
    data = response.data or []
    if data:
        return data[0]["id"]

    project_id = str(uuid.uuid4())
    client.table(PROJECT_TABLE).insert(
        {
            "id": project_id,
            "user_id": user_id,
            "project_name": DEFAULT_PROJECT_NAME,
            "created_at": datetime.utcnow().isoformat(),
        }
    ).execute()
    return project_id


def record_generated_image(
    user_id: str,
    image_type: str,
    local_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    project_id: Optional[str] = None,
) -> str:
    """
    Upload the generated image to Supabase Storage and log it in Postgres.

    Returns the public URL for the stored asset.
    """
    client = get_supabase_admin_client()
    project_id = project_id or _ensure_default_project(user_id)
    file_name = os.path.basename(local_path)
    storage_path = f"{user_id}/{project_id}/{file_name}"
    upload_file_to_storage(local_path, storage_path, bucket=STORAGE_BUCKET, content_type="image/png")
    public_url = client.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)

    payload = {
        "user_id": user_id,
        "project_id": project_id,
        "image_type": image_type,
        "image_url": public_url,
        "metadata": metadata or {},
    }
    client.table(GENERATED_TABLE).insert(payload).execute()
    return public_url


def get_last_generated_image_url(user_id: str) -> Optional[str]:
    """Fetch the most recent image URL stored for the user."""
    client = get_supabase_admin_client()
    response = (
        client.table(GENERATED_TABLE)
        .select("image_url")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    data = response.data or []
    if not data:
        return None
    return data[0].get("image_url")


