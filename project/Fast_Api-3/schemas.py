from typing import List

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator


class BranchCreate(BaseModel):
    name: str = Field(min_length=1)
    city: str = Field(min_length=1)

    @field_validator("name", "city")
    @classmethod
    def not_blank(cls, v):
        if not v.strip():
            raise ValueError("must not be blank")
        return v


class BranchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str


class MembershipPlanCreate(BaseModel):
    name: str = Field(min_length=1)
    duration_months: StrictInt = Field(ge=1)
    monthly_fee: StrictInt = Field(ge=300)
    guest_passes: StrictInt = Field(ge=0)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("name must not be blank")
        return v


class MembershipPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    duration_months: int
    monthly_fee: int
    guest_passes: int


class BranchWithPlans(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str
    membership_plans: List[MembershipPlanOut]