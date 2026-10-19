"""PawPal+ core system: owners, pets, tasks, and the scheduler (see diagrams/uml_draft.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from itertools import combinations

# Lower number = more important. Used to rank Task.priority strings.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# How often a task repeats.
FREQUENCIES = ("once", "daily", "weekly")

# How far ahead the next copy of a recurring task is due.
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    description: str
    due_time: datetime
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    frequency: str = "once"  # "once", "daily", or "weekly"
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task()

    def __post_init__(self) -> None:
        """Normalize priority and reject values the scheduler can't use."""
        self.priority = self.priority.strip().lower()
        if self.priority not in PRIORITY_RANK:
            raise ValueError(
                f"priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}"
            )
        self.frequency = self.frequency.strip().lower()
        if self.frequency not in FREQUENCIES:
            raise ValueError(
                f"frequency must be one of {list(FREQUENCIES)}, got {self.frequency!r}"
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """A pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Plans an owner's day using the tasks from all of their pets.

    All task data comes from Owner.get_all_tasks(), so every pet is included.
    """

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans for the given owner."""
        self.owner = owner

    def _end_time(self, task: Task) -> datetime:
        """Return when a task finishes (due_time + duration_minutes)."""
        return task.due_time + timedelta(minutes=task.duration_minutes)

    def _pending_tasks(self, day: date | None) -> list[Task]:
        """Return incomplete tasks, limited to one day if given."""
        return [
            task
            for task in self.owner.get_all_tasks()
            if not task.completed and (day is None or task.due_time.date() == day)
        ]

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by due time."""
        # due_time is a datetime, so it sorts by date and time directly. Times
        # stored as "HH:MM" strings would also sort correctly with the same key,
        # as long as they are zero-padded ("08:00", not "8:00").
        return sorted(self.owner.get_all_tasks(), key=lambda task: task.due_time)

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        return [
            task
            for task in self.owner.get_all_tasks()
            if (pet_name is None or task.pet_name.lower() == pet_name.lower())
            and (completed is None or task.completed == completed)
        ]

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task and, if it repeats, add its next occurrence to the same pet."""
        if task.completed:
            return None  # already done, so don't create a duplicate next copy
        # Find the pet that owns this exact task object.
        pet = next(
            (p for p in self.owner.pets if any(t is task for t in p.tasks)), None
        )
        if pet is None:
            raise ValueError(f"'{task.description}' doesn't belong to any of this owner's pets")

        task.mark_complete()
        interval = RECURRENCE_INTERVALS.get(task.frequency)
        if interval is None:
            return None  # "once" tasks don't repeat
        next_task = replace(task, due_time=task.due_time + interval, completed=False)
        pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, day: date | None = None) -> list[str]:
        """Return warning messages for unfinished tasks whose times overlap, optionally on one day."""
        # Sorted by time, so in each pair task_b never starts before task_a.
        # They clash if task_b starts before task_a ends. This checks every
        # pair, which is simple and plenty fast for a day of pet tasks.
        tasks = sorted(self._pending_tasks(day), key=lambda task: task.due_time)
        warnings = []
        for task_a, task_b in combinations(tasks, 2):
            if task_b.due_time < self._end_time(task_a):
                warnings.append(self._conflict_message(task_a, task_b))
        return warnings

    def _conflict_message(self, task_a: Task, task_b: Task) -> str:
        """Describe how two overlapping tasks clash."""
        relation = (
            "is at the same time as"
            if task_a.due_time == task_b.due_time
            else "overlaps"
        )
        return (
            f"{task_a.pet_name}'s '{task_a.description}' "
            f"({task_a.due_time:%H:%M}-{self._end_time(task_a):%H:%M}) {relation} "
            f"{task_b.pet_name}'s '{task_b.description}' "
            f"({task_b.due_time:%H:%M}-{self._end_time(task_b):%H:%M})"
        )

    def generate_daily_plan(self, day: date | None = None) -> list[Task]:
        """Pick the highest-priority tasks that fit in the owner's available minutes."""
        # Completed tasks are skipped; if day is given, only that day's tasks count.
        candidates = sorted(
            self._pending_tasks(day),
            key=lambda task: (PRIORITY_RANK[task.priority], task.due_time),
        )
        plan = []
        minutes_left = self.owner.available_minutes
        for task in candidates:
            if task.duration_minutes <= minutes_left:
                plan.append(task)
                minutes_left -= task.duration_minutes
        # Show the chosen tasks in the order they happen.
        return sorted(plan, key=lambda task: task.due_time)

    def explain_plan(self, plan: list[Task], day: date | None = None) -> str:
        """Explain why each task was included and which tasks were left out."""
        planned_ids = {id(task) for task in plan}
        used = sum(task.duration_minutes for task in plan)
        minutes_left = self.owner.available_minutes - used

        lines = [
            f"Plan for {self.owner.name}: {len(plan)} task(s), "
            f"{used} of {self.owner.available_minutes} minutes used.",
            "Tasks are picked by priority (high, then medium, then low); "
            "ties go to the earlier task.",
        ]
        for task in plan:
            lines.append(
                f"- {task.due_time:%H:%M} {task.description} ({task.pet_name}, "
                f"{task.priority} priority, {task.duration_minutes} min): "
                "included, it fit in the remaining time."
            )

        skipped = [
            task for task in self._pending_tasks(day) if id(task) not in planned_ids
        ]
        for task in sorted(skipped, key=lambda task: task.due_time):
            lines.append(
                f"- Skipped {task.description} ({task.pet_name}, {task.priority} "
                f"priority, {task.duration_minutes} min): needed "
                f"{task.duration_minutes} min but only {minutes_left} were left."
            )

        conflicts = self.detect_conflicts(day)
        if conflicts:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in conflicts)
        return "\n".join(lines)
