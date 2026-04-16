"""Unit tests for stashenv.crypto."""

import pytest
from stashenv.crypto import encrypt, decrypt


SAMPLE = "DB_HOST=localhost\nDB_PASS=secret\n"
PASSWORD = "hunter2"


def test_encrypt_returns_bytes():
    result = encrypt(SAMPLE, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    payload = encrypt(SAMPLE, PASSWORD)
    recovered = decrypt(payload, PASSWORD)
    assert recovered == SAMPLE


def test_different_encryptions_differ():
    """Each encryption should produce a unique ciphertext (random salt)."""
    a = encrypt(SAMPLE, PASSWORD)
    b = encrypt(SAMPLE, PASSWORD)
    assert a != b


def test_wrong_password_raises():
    payload = encrypt(SAMPLE, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(payload, "wrongpassword")


def test_corrupted_data_raises():
    payload = bytearray(encrypt(SAMPLE, PASSWORD))
    payload[20] ^= 0xFF  # flip a byte
    with pytest.raises(ValueError):
        decrypt(bytes(payload), PASSWORD)
