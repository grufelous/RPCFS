from typing import Any

from utils.config import LIST_DELIMITER


def encode_data(data: Any) -> bytes:
    return str(data).encode()


def decode_data(data: bytes) -> str:
    return data.decode()


def serialize_list(data: list) -> str:
    return LIST_DELIMITER.join(data)


def deserialize_list(data: str) -> list:
    return data.split(LIST_DELIMITER)
