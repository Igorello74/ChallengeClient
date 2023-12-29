from typing import Any, TypeVar

import jsons  # type: ignore

from .errors import DeserializationError

T = TypeVar('T')


def serialize(obj: Any) -> str:
    """Serialize an obj to json

    Args:
        obj: an object of arbitary type (though dataclasses are preferred the most)

    Returns:
        A string with the json representation of the object
    """
    return jsons.dumps(obj, key_transformer=jsons.KEY_TRANSFORMER_CAMELCASE)


def deserialize(s: str, cls: type[T]) -> T:
    """Deserialize json data into the given type

    Args:
        s: the json string to deserialize
        cls: the target type of deserialization (must be a class or, better, a dataclass)

    Raises:
        DeserializationError: if deserialization failed for some reason.

    Returns:
        an instance of cls
    """
    try:
        return jsons.loads(
            s, cls, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)
    except Exception as e:
        raise DeserializationError(s, cls) from e
