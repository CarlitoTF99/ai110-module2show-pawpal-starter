"""Tests for the PawPal+ core classes."""

from datetime import date, datetime

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 10, 18)


def make_task() -> Task:
    """Return a simple task for tests."""
    return Task("Morning walk", datetime(2026, 10, 18, 8, 0), 30, "high")


def at(hour: int, minute: int = 0, day: int = 18) -> datetime:
    """Return a datetime on October `day`, 2026."""
    return datetime(2026, 10, day, hour, minute)


def make_owner(minutes: int = 120) -> tuple[Owner, Pet, Pet, Scheduler]:
    """Return an owner with two pets (no tasks) and a scheduler for them."""
    rex = Pet("Rex", "dog")
    milo = Pet("Milo", "cat")
    owner = Owner("Jose", minutes)
    owner.add_pet(rex)
    owner.add_pet(milo)
    return owner, rex, milo, Scheduler(owner)


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Rex", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task())

    assert len(pet.get_tasks()) == 1


# --- Sorting ---------------------------------------------------------------


def test_sort_by_time_orders_tasks_added_out_of_order():
    _, rex, milo, scheduler = make_owner()
    rex.add_task(Task("Dinner", at(18), 10, "high"))
    milo.add_task(Task("Breakfast", at(7), 10, "high"))
    rex.add_task(Task("Walk", at(12), 30, "medium"))

    times = [task.due_time for task in scheduler.sort_by_time()]

    assert times == [at(7), at(12), at(18)]


def test_sort_by_time_with_no_tasks_returns_empty_list():
    _, _, _, scheduler = make_owner()

    assert scheduler.sort_by_time() == []


# --- Filtering -------------------------------------------------------------


def test_filter_by_pet_name_ignores_case():
    _, rex, milo, scheduler = make_owner()
    rex.add_task(Task("Walk", at(8), 30, "high"))
    milo.add_task(Task("Meds", at(9), 5, "high"))

    tasks = scheduler.filter_tasks(pet_name="milo")

    assert [task.description for task in tasks] == ["Meds"]


def test_filter_by_completion_status():
    _, rex, _, scheduler = make_owner()
    walk = Task("Walk", at(8), 30, "high")
    rex.add_task(walk)
    rex.add_task(Task("Dinner", at(18), 10, "high"))
    walk.mark_complete()

    assert scheduler.filter_tasks(completed=True) == [walk]
    assert [t.description for t in scheduler.filter_tasks(completed=False)] == ["Dinner"]


def test_filter_by_pet_and_status_together():
    _, rex, milo, scheduler = make_owner()
    rex_walk = Task("Walk", at(8), 30, "high")
    rex.add_task(rex_walk)
    rex.add_task(Task("Dinner", at(18), 10, "high"))
    milo_meds = Task("Meds", at(9), 5, "high")
    milo.add_task(milo_meds)
    rex_walk.mark_complete()
    milo_meds.mark_complete()

    assert scheduler.filter_tasks(pet_name="Rex", completed=True) == [rex_walk]


def test_filter_with_no_filters_returns_every_pets_tasks():
    _, rex, milo, scheduler = make_owner()
    rex.add_task(Task("Walk", at(8), 30, "high"))
    milo.add_task(Task("Meds", at(9), 5, "high"))

    assert len(scheduler.filter_tasks()) == 2


# --- Recurring tasks -------------------------------------------------------


def test_completing_daily_task_creates_next_day_copy():
    _, rex, _, scheduler = make_owner()
    walk = Task("Walk", at(8), 30, "high", "daily")
    rex.add_task(walk)

    next_walk = scheduler.mark_task_complete(walk)

    assert walk.completed is True
    assert next_walk is not walk
    assert next_walk.due_time == at(8, day=19)
    assert next_walk.completed is False
    assert next_walk.pet_name == "Rex"
    assert any(task is next_walk for task in rex.get_tasks())


def test_completing_weekly_task_creates_copy_seven_days_later():
    _, rex, _, scheduler = make_owner()
    bath = Task("Bath", at(15), 30, "low", "weekly")
    rex.add_task(bath)

    next_bath = scheduler.mark_task_complete(bath)

    assert next_bath.due_time == at(15, day=25)


def test_daily_task_rolls_over_to_next_month():
    _, rex, _, scheduler = make_owner()
    walk = Task("Walk", datetime(2026, 10, 31, 8, 0), 30, "high", "daily")
    rex.add_task(walk)

    next_walk = scheduler.mark_task_complete(walk)

    assert next_walk.due_time == datetime(2026, 11, 1, 8, 0)


def test_completing_once_task_does_not_create_copy():
    _, rex, _, scheduler = make_owner()
    vet = Task("Vet", at(9), 60, "high")
    rex.add_task(vet)

    assert scheduler.mark_task_complete(vet) is None
    assert vet.completed is True
    assert len(rex.get_tasks()) == 1


def test_completing_same_task_twice_does_not_duplicate():
    _, rex, _, scheduler = make_owner()
    walk = Task("Walk", at(8), 30, "high", "daily")
    rex.add_task(walk)

    scheduler.mark_task_complete(walk)
    assert scheduler.mark_task_complete(walk) is None
    assert len(rex.get_tasks()) == 2


def test_completing_task_from_another_owner_raises_error():
    _, _, _, scheduler = make_owner()
    stray = Task("Stray", at(8), 10, "low", "daily")

    with pytest.raises(ValueError):
        scheduler.mark_task_complete(stray)


# --- Conflict detection ----------------------------------------------------


def test_tasks_at_same_time_for_different_pets_conflict():
    _, rex, milo, scheduler = make_owner()
    rex.add_task(Task("Breakfast", at(7, 30), 10, "high"))
    milo.add_task(Task("Breakfast", at(7, 30), 10, "high"))

    warnings = scheduler.detect_conflicts(DAY)

    assert len(warnings) == 1
    assert "same time" in warnings[0]


def test_overlapping_tasks_for_same_pet_conflict():
    _, rex, _, scheduler = make_owner()
    rex.add_task(Task("Walk", at(8), 30, "high"))
    rex.add_task(Task("Brushing", at(8, 15), 10, "low"))

    warnings = scheduler.detect_conflicts(DAY)

    assert len(warnings) == 1
    assert "overlaps" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    _, rex, _, scheduler = make_owner()
    rex.add_task(Task("Walk", at(8), 30, "high"))
    rex.add_task(Task("Dinner", at(8, 30), 10, "high"))

    assert scheduler.detect_conflicts(DAY) == []


def test_completed_tasks_are_ignored_for_conflicts():
    _, rex, milo, scheduler = make_owner()
    walk = Task("Walk", at(8), 30, "high")
    rex.add_task(walk)
    milo.add_task(Task("Meds", at(8), 5, "high"))
    walk.mark_complete()

    assert scheduler.detect_conflicts(DAY) == []


def test_conflicts_on_other_days_are_excluded_when_day_given():
    _, rex, milo, scheduler = make_owner()
    rex.add_task(Task("Vet", at(9, day=19), 60, "high"))
    milo.add_task(Task("Groom", at(9, 30, day=19), 20, "low"))

    assert scheduler.detect_conflicts(DAY) == []
    assert len(scheduler.detect_conflicts()) == 1


def test_no_tasks_means_no_conflicts():
    _, _, _, scheduler = make_owner()

    assert scheduler.detect_conflicts(DAY) == []


# --- Daily plan ------------------------------------------------------------


def test_daily_plan_picks_high_priority_first_within_time_limit():
    _, rex, milo, scheduler = make_owner(minutes=40)
    # Earliest task is low priority, so a plan that just goes in time order
    # would pick Grooming and fail this test.
    rex.add_task(Task("Grooming", at(7), 30, "low"))
    milo.add_task(Task("Meds", at(10), 10, "high"))
    rex.add_task(Task("Walk", at(8), 30, "high"))

    plan = scheduler.generate_daily_plan(DAY)

    assert [task.description for task in plan] == ["Walk", "Meds"]


def test_daily_plan_skips_completed_tasks_and_other_days():
    _, rex, _, scheduler = make_owner()
    done = Task("Breakfast", at(7), 10, "high")
    rex.add_task(done)
    done.mark_complete()
    rex.add_task(Task("Vet", at(9, day=19), 60, "high"))
    rex.add_task(Task("Walk", at(8), 30, "high"))

    plan = scheduler.generate_daily_plan(DAY)

    assert [task.description for task in plan] == ["Walk"]
