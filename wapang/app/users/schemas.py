import re

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from wapang.common.exceptions import InvalidFormatException, MissingRequiredFieldException

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password", mode="after")
    def validate_password(cls, v) -> str:
        if len(v) < 8 or len(v) > 20:
            raise InvalidFormatException()
        return v

class UserUpdateRequest(BaseModel):
    nickname: str | None = None
    address: str | None = None
    phone_number: str | None = None

    @field_validator("nickname", mode="after")
    def validate_nickname(cls, v):
        if v is not None and len(v) > 20:
            raise InvalidFormatException()
        return v

    @field_validator("address", mode="after")
    def validate_address(cls, v):
        if v is not None and len(v) > 100:
            raise InvalidFormatException()
        return v

    @field_validator("phone_number", mode="after")
    def validate_phone_number(cls, v):
        if v is not None and re.fullmatch(r"010-\d{4}-\d{4}", v) is None:
            raise InvalidFormatException()
        return v

    @model_validator(mode="after")
    def validate_not_empty(self):
        if self.nickname is None and self.address is None and self.phone_number is None:
            raise MissingRequiredFieldException()
        return self

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    nickname: str | None
    address: str | None
    phone_number: str | None
    
    model_config = ConfigDict(from_attributes=True)