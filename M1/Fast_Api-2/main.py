import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(engine)
app = FastAPI()


@app.post("/skill-groups", response_model=schemas.SkillGroupOut, status_code=201)
def create_skill_group(payload: schemas.SkillGroupCreate, db: Session = Depends(get_db)):
    group = models.SkillGroup(**payload.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@app.post(
    "/skill-groups/{parent_id}/trainers",
    response_model=schemas.TrainerOut,
    status_code=201,
)
def create_trainer(parent_id: int, payload: schemas.TrainerCreate, db: Session = Depends(get_db)):
    group = db.query(models.SkillGroup).filter(models.SkillGroup.id == parent_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Skill group not found")

    trainer = models.Trainer(**payload.model_dump(), skillgroup_id=parent_id)
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer


@app.get("/skill-groups/{parent_id}", response_model=schemas.SkillGroupWithTrainers)
def get_skill_group(
    parent_id: int,
    designation: str | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
):
    group = db.query(models.SkillGroup).filter(models.SkillGroup.id == parent_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Skill group not found")

    query = db.query(models.Trainer).filter(models.Trainer.skillgroup_id == parent_id)

    # Blank or missing designation = no filter; otherwise exact match
    if designation is not None and designation.strip() != "":
        query = query.filter(models.Trainer.designation == designation)

    if sort is not None:
        if sort == "name":
            query = query.order_by(models.Trainer.name.asc(), models.Trainer.id.asc())
        elif sort == "session_fee":
            query = query.order_by(models.Trainer.session_fee.asc(), models.Trainer.id.asc())
        else:
            raise HTTPException(status_code=404, detail="Invalid sort field")
    else:
        query = query.order_by(models.Trainer.id.asc())

    return {
        "id": group.id,
        "name": group.name,
        "floor_number": group.floor_number,
        "trainers": query.all(),
    }


@app.put(
    "/skill-groups/{parent_id}/trainers/{child_id}",
    response_model=schemas.TrainerOut,
    status_code=200,
)
def update_trainer(
    parent_id: int,
    child_id: int,
    payload: schemas.TrainerCreate,
    db: Session = Depends(get_db),
):
    group = db.query(models.SkillGroup).filter(models.SkillGroup.id == parent_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Skill group not found")

    trainer = db.query(models.Trainer).filter(models.Trainer.id == child_id).first()
    if trainer is None or trainer.skillgroup_id != parent_id:
        raise HTTPException(status_code=404, detail="Trainer not found")

    trainer.name = payload.name
    trainer.designation = payload.designation
    trainer.session_fee = payload.session_fee
    trainer.experience_years = payload.experience_years

    db.commit()
    db.refresh(trainer)
    return trainer


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)