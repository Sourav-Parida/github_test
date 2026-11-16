from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillGroupCreate(BaseModel):
    name: str = Field(min_length=1)
    floor_number: int = Field(ge=1)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("name must not be blank")
        return v


class SkillGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    floor_number: int


class TrainerCreate(BaseModel):
    name: str = Field(min_length=1)
    designation: str = Field(min_length=1)
    session_fee: int = Field(ge=300)
    experience_years: int = Field(ge=0)

    @field_validator("name", "designation")
    @classmethod
    def not_blank(cls, v):
        if not v.strip():
            raise ValueError("must not be blank")
        return v


class TrainerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    designation: str
    session_fee: int
    experience_years: int


class SkillGroupWithTrainers(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    floor_number: int
    trainers: List[TrainerOut]