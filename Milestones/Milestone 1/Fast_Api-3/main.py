import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(engine)
app = FastAPI()


@app.post("/branches", response_model=schemas.BranchOut, status_code=201)
def create_branch(payload: schemas.BranchCreate, db: Session = Depends(get_db)):
    branch = models.GymBranch(**payload.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@app.post(
    "/branches/{parent_id}/membership_plans",
    response_model=schemas.MembershipPlanOut,
    status_code=201,
)
def create_plan(parent_id: int, payload: schemas.MembershipPlanCreate, db: Session = Depends(get_db)):
    branch = db.query(models.GymBranch).filter(models.GymBranch.id == parent_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    plan = models.MembershipPlan(**payload.model_dump(), branch_id=parent_id)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@app.get("/branches/{parent_id}", response_model=schemas.BranchWithPlans)
def get_branch(
    parent_id: int,
    duration_months: str | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
):
    branch = db.query(models.GymBranch).filter(models.GymBranch.id == parent_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    query = db.query(models.MembershipPlan).filter(models.MembershipPlan.branch_id == parent_id)

    # Missing or blank duration_months = no filter; otherwise exact match
    if duration_months is not None and duration_months.strip() != "":
        try:
            months = int(duration_months.strip())
        except ValueError:
            raise HTTPException(status_code=422, detail="duration_months must be an integer")
        query = query.filter(models.MembershipPlan.duration_months == months)

    if sort is not None:
        if sort == "name":
            query = query.order_by(models.MembershipPlan.name.asc(), models.MembershipPlan.id.asc())
        elif sort == "monthly_fee":
            query = query.order_by(models.MembershipPlan.monthly_fee.asc(), models.MembershipPlan.id.asc())
        else:
            raise HTTPException(status_code=404, detail="Invalid sort field")
    else:
        query = query.order_by(models.MembershipPlan.id.asc())

    return {
        "id": branch.id,
        "name": branch.name,
        "city": branch.city,
        "membership_plans": query.all(),
    }


@app.put(
    "/branches/{parent_id}/membership_plans/{child_id}",
    response_model=schemas.MembershipPlanOut,
    status_code=200,
)
def update_plan(
    parent_id: int,
    child_id: int,
    payload: schemas.MembershipPlanCreate,
    db: Session = Depends(get_db),
):
    branch = db.query(models.GymBranch).filter(models.GymBranch.id == parent_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    plan = db.query(models.MembershipPlan).filter(models.MembershipPlan.id == child_id).first()
    if plan is None or plan.branch_id != parent_id:
        raise HTTPException(status_code=404, detail="Membership plan not found")

    plan.name = payload.name
    plan.duration_months = payload.duration_months
    plan.monthly_fee = payload.monthly_fee
    plan.guest_passes = payload.guest_passes

    db.commit()
    db.refresh(plan)
    return plan


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)