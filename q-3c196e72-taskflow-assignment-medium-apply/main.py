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
    """Seed the repo, then apply ops in order."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Seed initial tasks
        for r in seed:
            session.add(
                Task(
                    title=r["title"],
                    status=r.get("status", "todo")
                )
            )
        session.commit()

        # Apply operations in order
        for op in ops:
            kind = op["op"]

            if kind == "create":
                task = Task(
                    title=op["title"],
                    status=op.get("status", "todo")
                )
                session.add(task)

            elif kind == "update_status":
                task = session.get(Task, op["id"])
                if task is not None:
                    task.status = op["status"]

            elif kind == "rename":
                task = session.get(Task, op["id"])
                if task is not None:
                    task.title = op["title"]

            elif kind == "delete":
                task = session.get(Task, op["id"])
                if task is not None:
                    session.delete(task)

        # Save all operations
        session.commit()

        # Retrieve tasks sorted by ID
        tasks = session.query(Task).order_by(Task.id).all()

        result = [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status
            }
            for task in tasks
        ]

        return {
            "count": len(result),
            "tasks": result
        }