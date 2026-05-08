"""
Core domain objects for the todo app: date helpers, TodoItem model, and
the TodoApp manager that handles persistence plus CRUD operations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional


def _coerce_due_date(value: Optional[str | datetime]) -> Optional[datetime]:
    """Accept a datetime or an ISO-like string and normalize to datetime."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    value = value.strip()
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        "Could not parse due date. Use YYYY-MM-DD or YYYY-MM-DD HH:MM format."
    )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if value in (None, ""):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@dataclass(slots=True)
class TodoItem:
    task_id: int
    title: str
    description: str = ""
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def mark_complete(self) -> None:
        self.completed = True
        self.updated_at = _utcnow()

    def mark_incomplete(self) -> None:
        self.completed = False
        self.updated_at = _utcnow()

    def update(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str | datetime] = None,
    ) -> None:
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty.")
            self.title = title.strip()
        if description is not None:
            self.description = description.strip()
        if due_date is not None:
            self.due_date = _coerce_due_date(due_date)
        self.updated_at = _utcnow()

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "TodoItem":
        return cls(
            task_id=int(payload["task_id"]),
            title=payload.get("title", ""),
            description=payload.get("description", ""),
            due_date=_parse_timestamp(payload.get("due_date")),
            completed=bool(payload.get("completed", False)),
            created_at=_parse_timestamp(payload.get("created_at")) or _utcnow(),
            updated_at=_parse_timestamp(payload.get("updated_at")) or _utcnow(),
        )


class TodoApp:
    """Core todo logic without any UI coupling."""

    def __init__(self, storage_path: Optional[str | Path] = None) -> None:
        self._tasks: List[TodoItem] = []
        self._next_id = 1
        self._storage_path = (
            Path(storage_path).expanduser() if storage_path else None
        )
        self._load()

    def _generate_id(self) -> int:
        current = self._next_id
        self._next_id += 1
        return current

    def _serialize(self) -> dict:
        return {
            "next_id": self._next_id,
            "tasks": [task.to_dict() for task in self._tasks],
        }

    def _save(self) -> None:
        if not self._storage_path:
            return
        payload = self._serialize()
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._storage_path.write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )
        except OSError:
            pass

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        tasks: List[TodoItem] = []
        for entry in raw.get("tasks", []):
            try:
                tasks.append(TodoItem.from_dict(entry))
            except (KeyError, TypeError, ValueError):
                continue
        self._tasks = tasks
        stored_next = raw.get("next_id")
        if isinstance(stored_next, int) and stored_next > self._next_id:
            self._next_id = stored_next
        elif self._tasks:
            self._next_id = max(task.task_id for task in self._tasks) + 1

    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str | datetime] = None,
    ) -> TodoItem:
        title = title.strip()
        if not title:
            raise ValueError("Task title is required.")
        task = TodoItem(
            task_id=self._generate_id(),
            title=title,
            description=description.strip(),
            due_date=_coerce_due_date(due_date),
        )
        self._tasks.append(task)
        self._save()
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[TodoItem]:
        """Return tasks, optionally filtered by status."""
        if status is None or status == "all":
            return list(self._tasks)
        if status == "pending":
            return [task for task in self._tasks if not task.completed]
        if status == "completed":
            return [task for task in self._tasks if task.completed]
        raise ValueError("Status must be one of: None, 'all', 'pending', 'completed'.")

    def find_by_id(self, task_id: int) -> TodoItem:
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        raise LookupError(f"No task with id={task_id}.")

    def mark_complete(self, task_id: int) -> None:
        self.find_by_id(task_id).mark_complete()
        self._save()

    def mark_incomplete(self, task_id: int) -> None:
        self.find_by_id(task_id).mark_incomplete()
        self._save()

    def update_task(
        self,
        task_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str | datetime] = None,
    ) -> None:
        self.find_by_id(task_id).update(
            title=title,
            description=description,
            due_date=due_date,
        )
        self._save()

    def delete_task(self, task_id: int) -> None:
        task = self.find_by_id(task_id)
        self._tasks.remove(task)
        self._save()

    def search(self, keyword: str) -> List[TodoItem]:
        keyword_lower = keyword.lower()
        return [
            task
            for task in self._tasks
            if keyword_lower in task.title.lower()
            or keyword_lower in task.description.lower()
        ]

    def purge_completed(self) -> int:
        """Remove all completed tasks; return the number removed."""
        completed = [task for task in self._tasks if task.completed]
        for task in completed:
            self._tasks.remove(task)
        if completed:
            self._save()
        return len(completed)

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self) -> Iterable[TodoItem]:
        return iter(self._tasks)


__all__ = ["TodoApp", "TodoItem"]
