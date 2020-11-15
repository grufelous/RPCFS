from typing import Any


def encode_data(data: Any) -> bytes:
    return str(data).encode()


def decode_data(data: bytes) -> str:
    return data.decode()
