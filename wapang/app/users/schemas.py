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

class StoreAddRequest(BaseModel):
    store_name: str
    address: str
    email: EmailStr
    phone_number: str
    delivery_fee: int

    @field_validator("store_name", mode="after")
    def validate_store_name(cls, v):
        if len(v) > 20 or len(v) < 3:
            raise InvalidFormatException()
        return v

    @field_validator("address", mode="after")
    def validate_address(cls, v):
        if len(v) > 100:
            raise InvalidFormatException()
        return v
    
    @field_validator("phone_number", mode="after")
    def validate_phone_number(cls, v):
        if re.fullmatch(r"010-\d{4}-\d{4}", v) is None:
            raise InvalidFormatException()
        return v

    @field_validator("delivaey_fee", mode="after")
    def validate_delivery_fee(cls, v):
        if v < 0:
            raise InvalidFormatException()
        return v
    
class StoreUpdateRequest(BaseModel):
    email: EmailStr | None = None
    store_name: str | None = None
    address: str | None = None
    phone_number: str | None = None
    delivery_fee: int | None = None

    @field_validator("store_name", mode="after")
    def validate_store_name(cls, v):
        if v is not None and (len(v) > 20 or len(v) < 3):
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

    @field_validator("delivery_fee", mode="after")
    def validate_delivery_fee(cls, v):
        if v is not None and v < 0:
            raise InvalidFormatException()
        return v

    @model_validator(mode="after")
    def validate_not_empty(self):
        fields = [self.email, self.store_name, self.address, self.phone_number, self.delivery_fee]
        if all(field is None for field in fields):
            raise MissingRequiredFieldException()
        return self

class StoreResponse(BaseModel):
    id: str
    store_name: str
    address: str
    email: EmailStr 
    phone_number: str
    delivery_fee: int

    # SQLAlchemy로 DB에서 조회한 store 객체를 딕셔너리가 아닌 일반 파이썬 클래스 객체로 접근하기 위함.
    # pydantic이 일반 객체의 속성 (.id .email 등)에서도 값을 꺼낼 수 있도록 함. 
    model_config = ConfigDict(from_attributes = True)

class ItemResponse(BaseModel):
    id: str
    item_name: str
    price: int
    stock: int
    
    model_config = ConfigDict(from_attributes=True)