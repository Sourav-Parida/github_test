from sqlalchemy import create_engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="todo")


def insert_tasks(rows):
    """Create each row as a Task in a fresh in-memory SQLite DB, then
    return every stored task as a plain dict {"id","title","status"},
    ordered by id. Missing "status" should default to "todo"."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for row in rows:
            task = Task(
                title=row["title"],
                status=row.get("status", "todo")
            )
            session.add(task)

        session.commit()

        tasks = session.query(Task).order_by(Task.id).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status
            }
            for task in tasks
        ]