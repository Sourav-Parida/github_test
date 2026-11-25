from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PracticeAreaCreate(BaseModel):
    name: str = Field(min_length=1)
    floor_number: int = Field(ge=1)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("name must not be blank")
        return v  


class PracticeAreaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    floor_number: int


class ConsultantCreate(BaseModel):
    name: str = Field(min_length=1)
    designation: str = Field(min_length=1)
    consultation_fee: int = Field(ge=300)
    experience_years: int = Field(ge=0)

    @field_validator("name", "designation")
    @classmethod
    def not_blank(cls, v):
        if not v.strip():
            raise ValueError("must not be blank")
        return v

class ConsultantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    designation: str
    consultation_fee: int
    experience_years: int


class PracticeAreaWithConsultants(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    floor_number: int
    consultants: List[ConsultantOut]

