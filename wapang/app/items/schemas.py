from pydantic import BaseModel, ConfigDict, Field, model_validator

from wapang.common.exceptions import (
    InvalidFormatException,
    MissingRequiredFieldException,
)


class AddItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_name: str = Field(min_length=2, max_length=50)
    price: int = Field(ge=0, strict=True)
    stock: int = Field(ge=0, strict=True)


class UpdateItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_name: str | None = Field(default=None, min_length=2, max_length=50)
    price: int | None = Field(default=None, ge=0, strict=True)
    stock: int | None = Field(default=None, ge=0, strict=True)

    @model_validator(mode="after")
    def validate_patch_fields(self):
        if not self.model_fields_set:
            raise MissingRequiredFieldException()

        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise InvalidFormatException()

        return self


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    item_name: str
    price: int
    stock: int


class ItemListResponse(ItemResponse):
    store_id: str
    store_name: str
