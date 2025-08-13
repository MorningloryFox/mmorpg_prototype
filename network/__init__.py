"""Networking helpers for serializing and compressing packets."""

import json
import zlib
import base64


def encode(message: dict) -> bytes:
    """Serialize and compress a message for network transmission."""
    data = json.dumps(message).encode()
    compressed = zlib.compress(data)
    return base64.b64encode(compressed) + b"\n"


def decode(payload: str | bytes) -> dict:
    """Decode a previously :func:`encode`d message."""
    if isinstance(payload, str):
        payload_bytes = payload.strip().encode()
    else:
        payload_bytes = payload.strip()
    data = base64.b64decode(payload_bytes)
    text = zlib.decompress(data).decode()
    return json.loads(text)


__all__ = ["encode", "decode"]

