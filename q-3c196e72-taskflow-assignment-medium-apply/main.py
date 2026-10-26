from sqlalchemy import create_engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="todo")


def apply_ops(seed, ops):
    """Seed the repo, then apply ops in order. Each op is a dict with "op":
      - "create":        {"op":"create","title":..,"status":..}
      - "update_status": {"op":"update_status","id":..,"status":..}
      - "rename":        {"op":"rename","id":..,"title":..}
      - "delete":        {"op":"delete","id":..}
    Ops targeting a missing id are safe no-ops. Return
    {"count": <n>, "tasks": [ {"id","title","status"} sorted by id ]}."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        for r in seed:
            session.add(Task(title=r["title"], status=r.get("status", "todo")))
        session.commit()
        for op in ops:
            kind = op["op"]
            # TODO: handle "create", "update_status", "rename", "delete"
            pass
        # TODO: build and return the {"count","tasks"} summary