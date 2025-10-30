# backend_v2/app/models/pyobjectid.py
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Any
from bson import ObjectId

class PyObjectId(ObjectId):
    """
    Custom Pydantic type for MongoDB's ObjectId.
    Enables validation and serialization between str and ObjectId.
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Validates that the input is a valid ObjectId, either as a str or ObjectId.
        """
        def validate_from_str(value: str) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return ObjectId(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.with_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # Allow ObjectId instances to pass through
                    core_schema.is_instance_schema(ObjectId),
                    # Validate strings
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )