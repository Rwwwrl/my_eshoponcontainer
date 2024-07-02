from typing import Type

from pydantic import BaseModel

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator

__doc__ = """
ORIGINAL https://gist.github.com/imankulov/4051b7805ad737ace7d8de3d3f934d6b
"""


class PydanticType(TypeDecorator):
    """Pydantic type.
    SAVING:
    - Uses SQLAlchemy JSON type under the hood.
    - Acceps the pydantic model and converts it to a dict on save.
    - SQLAlchemy engine JSON-encodes the dict to a string.
    RETRIEVING:
    - Pulls the string from the database.
    - SQLAlchemy engine JSON-decodes the string to a dict.
    - Uses the dict to create a pydantic model.
    """

    impl = JSONB

    def __init__(self, pydantic_type: Type[BaseModel]):
        super().__init__()
        self._pydantic_type = pydantic_type

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        return self._pydantic_type.model_dump(value)

    def process_result_value(self, value, dialect):
        return self._pydantic_type.model_validate(value)
