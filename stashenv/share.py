"""Share profiles between users via encrypted export bundles."""

from __future__ import annotations

import json
import base64
from pathlib import Path
from typing import Optional

from stashenv.store import load_profile, save_profile
from stashenv.crypto import encrypt, decrypt


def create_share_bundle(
    project_dir: Path,
    profile: str,
    password: str,
    share_password: str,
    recipient: Optional[str] = None,
) -> bytes:
    """Encrypt a profile with a share password and return a portable bundle."""
    env_text = load_profile(project_dir, profile, password)
    ciphertext = encrypt(env_text.encode(), share_password)
    bundle = {
        "profile": profile,
        "recipient": recipient,
        "data": base64.b64encode(ciphertext).decode(),
    }
    return json.dumps(bundle).encode()


def write_share_bundle(
    project_dir: Path,
    profile: str,
    password: str,
    share_password: str,
    output_path: Path,
    recipient: Optional[str] = None,
) -> None:
    """Write a share bundle to a file."""
    bundle = create_share_bundle(project_dir, profile, password, share_password, recipient)
    output_path.write_bytes(bundle)


def import_share_bundle(
    bundle_path: Path,
    share_password: str,
    project_dir: Path,
    password: str,
    profile_override: Optional[str] = None,
) -> str:
    """Import a share bundle into the current project. Returns the profile name."""
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")

    bundle = json.loads(bundle_path.read_bytes())
    raw = base64.b64decode(bundle["data"])
    env_text = decrypt(raw, share_password).decode()

    profile_name = profile_override or bundle["profile"]
    save_profile(project_dir, profile_name, env_text, password)
    return profile_name
