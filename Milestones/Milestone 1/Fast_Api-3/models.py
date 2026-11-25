from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class GymBranch(Base):
    __tablename__ = "gym_branches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)

    membership_plans = relationship(
        "MembershipPlan", back_populates="branch", cascade="all, delete-orphan"
    )


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    duration_months = Column(Integer, nullable=False)
    monthly_fee = Column(Integer, nullable=False)
    guest_passes = Column(Integer, nullable=False)
    branch_id = Column(Integer, ForeignKey("gym_branches.id"), nullable=False)

    branch = relationship("GymBranch", back_populates="membership_plans")