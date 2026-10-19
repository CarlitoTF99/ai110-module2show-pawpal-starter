# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

PawPal+ plans an owner's pet care day across multiple pets. All the logic lives in `pawpal_system.py`, which has four classes:

- **`Task`** (dataclass): one care activity, with a description, due time, duration, priority (`high`/`medium`/`low`), frequency (`once`/`daily`/`weekly`) and a completed flag. It rejects invalid priorities, frequencies and durations, and `mark_complete()` marks it done.
- **`Pet`** (dataclass): a pet's name, species and task list. `add_task()` adds a task and tags it with the pet's name.
- **`Owner`** (dataclass): the owner's name, how many minutes they have for pet care, and their pets. `get_all_tasks()` returns every pet's tasks in one list.
- **`Scheduler`**: the "brain." It holds an `Owner` and gets all of its data through `owner.get_all_tasks()`, so every pet is included. It can:
  - sort tasks by time and filter them by pet or completion status
  - detect tasks whose times overlap
  - build a daily plan by picking the highest-priority unfinished tasks that fit in the owner's available minutes
  - explain why each task was included or skipped

**How they work together:** an `Owner` has many `Pet`s, and each `Pet` has many `Task`s. The `Scheduler` never reaches into a single pet. It asks the `Owner` for all tasks, so adding a pet automatically includes its tasks in the plan. `main.py` is a demo script that builds an owner with two pets and prints today's schedule. `tests/test_pawpal.py` holds the pytest tests. The class diagram is in `diagrams/`.

## 🖥️ Sample Output

Output from running `python main.py` (an owner with two pets and five tasks):

```text
Today's Schedule (Sunday, October 18)
========================================
08:00 AM  Morning walk       Rex    30 min  [high]
08:15 AM  Give meds          Milo    5 min  [high]
12:00 PM  Feather toy play   Milo   20 min  [medium]
05:30 PM  Brushing           Rex    15 min  [low]

Plan for Jose: 4 task(s), 70 of 90 minutes used.
Tasks are picked by priority (high, then medium, then low); ties go to the earlier task.
- 08:00 Morning walk (Rex, high priority, 30 min): included, it fit in the remaining time.
- 08:15 Give meds (Milo, high priority, 5 min): included, it fit in the remaining time.
- 12:00 Feather toy play (Milo, medium priority, 20 min): included, it fit in the remaining time.
- 17:30 Brushing (Rex, low priority, 15 min): included, it fit in the remaining time.
- Skipped Litter box clean (Milo, medium priority, 45 min): needed 45 min but only 20 were left.
Warnings:
- Rex's 'Morning walk' (08:00-08:30) overlaps Milo's 'Give meds' (08:15-08:20)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
