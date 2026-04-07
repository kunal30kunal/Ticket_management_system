from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# USER SCHEMAS

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Password cannot be blank")
        return value


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Password cannot be blank")
        return value


# AUTH TOKEN

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


# TICKET SCHEMAS

AllowedPriority = Literal["low", "medium", "high"]
AllowedStatus = Literal["open", "in_progress", "closed"]
AllowedCategory = Literal["bug", "feature", "support", "other"]


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    priority: AllowedPriority
    category: AllowedCategory

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be blank")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Description cannot be blank")
        return value


class TicketEdit(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    description: Optional[str] = Field(default=None, min_length=5)
    priority: Optional[AllowedPriority] = None
    category: Optional[AllowedCategory] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be blank")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Description cannot be blank")
        return value


class TicketStatusChange(BaseModel):
    status: AllowedStatus


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    category: str
    created_by: int
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ASSISTANT

class AssistantResponse(BaseModel):
    question: str
    answer: str