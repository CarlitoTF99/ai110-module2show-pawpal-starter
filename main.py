"""Demo script: build an owner with pets and tasks, then exercise the Scheduler."""

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task


def at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(date.today(), time(hour, minute))


def section(title: str) -> None:
    """Print a section heading."""
    print()
    print(title)
    print("=" * 40)


def print_tasks(tasks: list[Task]) -> None:
    """Print one line per task."""
    if not tasks:
        print("(none)")
    for task in tasks:
        status = "done" if task.completed else "todo"
        print(
            f"{task.due_time:%a %I:%M %p}  {task.description:<18} "
            f"{task.pet_name:<5} {task.frequency:<7} [{status}]"
        )


def main() -> None:
    owner = Owner("Jose", available_minutes=90)

    rex = Pet("Rex", "dog")
    milo = Pet("Milo", "cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Added out of order on purpose, to show that sorting works.
    milo.add_task(Task("Litter box clean", at(19), 45, "medium", "daily"))
    rex.add_task(Task("Brushing", at(17, 30), 15, "low", "weekly"))
    milo.add_task(Task("Feather toy play", at(12), 20, "medium"))
    rex.add_task(Task("Morning walk", at(8), 30, "high", "daily"))
    milo.add_task(Task("Give meds", at(8, 15), 5, "high", "daily"))
    # Two tasks at exactly the same time, to show conflict detection.
    rex.add_task(Task("Breakfast", at(7, 30), 10, "high", "daily"))
    milo.add_task(Task("Breakfast", at(7, 30), 10, "high", "daily"))

    scheduler = Scheduler(owner)
    today = date.today()

    section("Unsorted: as stored, pet by pet (get_all_tasks)")
    print_tasks(owner.get_all_tasks())

    section("Sorted by time (sort_by_time)")
    print_tasks(scheduler.sort_by_time())

    section("Only Milo's tasks (filter_tasks pet_name='Milo')")
    print_tasks(scheduler.filter_tasks(pet_name="Milo"))

    section("Conflict warnings for today (detect_conflicts)")
    conflicts = scheduler.detect_conflicts(today)
    for warning in conflicts:
        print(f"WARNING: {warning}")
    if not conflicts:
        print("No conflicts.")

    section(f"Today's Schedule ({today:%A, %B %d})")
    plan = scheduler.generate_daily_plan(today)
    for task in plan:
        print(
            f"{task.due_time:%I:%M %p}  {task.description:<18} "
            f"{task.pet_name:<5} {task.duration_minutes:>3} min  [{task.priority}]"
        )
    print()
    print(scheduler.explain_plan(plan, today))

    section("Recurring tasks (mark_task_complete)")
    walk = next(task for task in rex.get_tasks() if task.description == "Morning walk")
    next_walk = scheduler.mark_task_complete(walk)
    print(f"Completed Rex's '{walk.description}' due {walk.due_time:%a %I:%M %p}.")
    print(f"Next one was created automatically, due {next_walk.due_time:%a %I:%M %p}.")
    play = next(task for task in milo.get_tasks() if task.description == "Feather toy play")
    if scheduler.mark_task_complete(play) is None:
        print(f"Completed Milo's '{play.description}' (once), so no next one was created.")

    section("Completed tasks (filter_tasks completed=True)")
    print_tasks(scheduler.filter_tasks(completed=True))

    section("Rex's tasks still to do, sorted (filter + sort)")
    rex_todo = scheduler.filter_tasks(pet_name="Rex", completed=False)
    print_tasks(sorted(rex_todo, key=lambda task: task.due_time))


if __name__ == "__main__":
    main()
