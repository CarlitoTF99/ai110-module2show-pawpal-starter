"""Demo script: build an owner with pets and tasks, then print today's schedule."""

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task


def at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(date.today(), time(hour, minute))


def main() -> None:
    owner = Owner("Jose", available_minutes=90)

    rex = Pet("Rex", "dog")
    milo = Pet("Milo", "cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    rex.add_task(Task("Morning walk", at(8), 30, "high", "daily"))
    rex.add_task(Task("Brushing", at(17, 30), 15, "low", "weekly"))
    milo.add_task(Task("Give meds", at(8, 15), 5, "high", "daily"))
    milo.add_task(Task("Feather toy play", at(12), 20, "medium"))
    milo.add_task(Task("Litter box clean", at(19), 45, "medium", "daily"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(date.today())

    print(f"Today's Schedule ({date.today():%A, %B %d})")
    print("=" * 40)
    for task in plan:
        print(
            f"{task.due_time:%I:%M %p}  {task.description:<18} "
            f"{task.pet_name:<5} {task.duration_minutes:>3} min  [{task.priority}]"
        )
    print()
    print(scheduler.explain_plan(plan, date.today()))


if __name__ == "__main__":
    main()
