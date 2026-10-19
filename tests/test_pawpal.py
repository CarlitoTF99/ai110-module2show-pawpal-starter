"""Tests for the PawPal+ core classes."""

from datetime import datetime

from pawpal_system import Pet, Task


def make_task() -> Task:
    """Return a simple task for tests."""
    return Task("Morning walk", datetime(2026, 10, 18, 8, 0), 30, "high")


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
