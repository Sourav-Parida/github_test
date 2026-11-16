from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class SkillGroup(Base):
    __tablename__ = "skill_groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    floor_number = Column(Integer, nullable=False)

    trainers = relationship(
        "Trainer", back_populates="skill_group", cascade="all, delete-orphan"
    )


class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    session_fee = Column(Integer, nullable=False)
    experience_years = Column(Integer, nullable=False)
    skillgroup_id = Column(Integer, ForeignKey("skill_groups.id"), nullable=False)

    skill_group = relationship("SkillGroup", back_populates="trainers")