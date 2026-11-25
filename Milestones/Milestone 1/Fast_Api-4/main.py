from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(engine)
app = FastAPI()


@app.post("/practice-areas", response_model=schemas.PracticeAreaOut, status_code=201)
def create_practice_area(payload: schemas.PracticeAreaCreate, db: Session = Depends(get_db)):

    area = models.PracticeArea(**payload.model_dump())

    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@app.post(
    "/practice-areas/{parent_id}/consultants",
    response_model=schemas.ConsultantOut,
    status_code=201,
)
def create_consultant(parent_id: int, payload: schemas.ConsultantCreate, db: Session = Depends(get_db)):
    
    area = db.query(models.PracticeArea).filter(models.PracticeArea.id == parent_id).first()
    
    if area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")

    consultant = models.Consultant(**payload.model_dump(), practicearea_id=parent_id)

    db.add(consultant)
    db.commit()
    db.refresh(consultant)
    return consultant


@app.get("/practice-areas/{parent_id}", response_model=schemas.PracticeAreaWithConsultants)
def get_practice_area(
    parent_id: int,
    designation: str | None =None,
    sort: str | None =None,
    db: Session = Depends(get_db),
):
    area = db.query(models.PracticeArea).filter(models.PracticeArea.id == parent_id).first()
    if area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")

    query = db.query(models.Consultant).filter(models.Consultant.practicearea_id == parent_id)

    # Blank or missing designation = no filter; otherwise exact match
    if designation is not None and designation.strip() != "":
        query = query.filter(models.Consultant.designation == designation)

    if sort is not None:
        if sort == "name":
            query = query.order_by(models.Consultant.name.asc(), models.Consultant.id.asc())
        elif sort == "consultation_fee":
            query = query.order_by(models.Consultant.consultation_fee.asc(), models.Consultant.id.asc())
        else:
            raise HTTPException(status_code=404, detail="Invalid sort field")
    else:
        query = query.order_by(models.Consultant.id.asc())

    return {
        "id":area.id,
        "name":area.name,
        "floor_number":area.floor_number,
        "consultants":query.all()
    }


@app.put(
    "/practice-areas/{parent_id}/consultants/{child_id}",
    response_model=schemas.ConsultantOut,
    status_code=200,
)
def update_consultant(
    parent_id: int,
    child_id: int,
    payload: schemas.ConsultantCreate,
    db: Session = Depends(get_db),
):
    area = db.query(models.PracticeArea).filter(models.PracticeArea.id == parent_id).first()


    if area is None:
        raise HTTPException(status_code=404, detail="Practice area not found")

    consultant = db.query(models.Consultant).filter(models.Consultant.id == child_id).first()
    if consultant is None or consultant.practicearea_id != parent_id:
        raise HTTPException(status_code=404, detail="Consultant not found")
    
    # consultant = models.Consultant(**payload.model_dump(), practicearea_id=parent_id)

    consultant.name = payload.name
    consultant.designation = payload.designation
    consultant.consultation_fee = payload.consultation_fee
    consultant.experience_years = payload.experience_years

    db.commit()
    db.refresh(consultant)

    return consultant


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8081)