from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PracticeAreaCreate(BaseModel):
    name: str = Field(min_length=1)
    floor_number: int = Field(ge=1)




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

