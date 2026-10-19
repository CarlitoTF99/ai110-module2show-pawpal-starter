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
  - complete tasks, automatically adding the next copy of daily and weekly tasks
  - detect tasks whose times overlap
  - build a daily plan by picking the highest-priority unfinished tasks that fit in the owner's available minutes
  - explain why each task was included or skipped

**How they work together:** an `Owner` has many `Pet`s, and each `Pet` has many `Task`s. The `Scheduler` never reaches into a single pet. It asks the `Owner` for all tasks, so adding a pet automatically includes its tasks in the plan. `main.py` is a demo script that builds an owner with two pets and shows sorting, filtering, conflict warnings, today's schedule and recurring tasks. `app.py` is the Streamlit UI for the same classes. `tests/test_pawpal.py` holds the pytest tests. The class diagram is in `diagrams/`.

## 🖥️ Sample Output

Output from running `python main.py` (an owner with two pets and seven tasks, added out of order):

```text
Unsorted: as stored, pet by pet (get_all_tasks)
========================================
Sun 05:30 PM  Brushing           Rex   weekly  [todo]
Sun 08:00 AM  Morning walk       Rex   daily   [todo]
Sun 07:30 AM  Breakfast          Rex   daily   [todo]
Sun 07:00 PM  Litter box clean   Milo  daily   [todo]
Sun 12:00 PM  Feather toy play   Milo  once    [todo]
Sun 08:15 AM  Give meds          Milo  daily   [todo]
Sun 07:30 AM  Breakfast          Milo  daily   [todo]

Sorted by time (sort_by_time)
========================================
Sun 07:30 AM  Breakfast          Rex   daily   [todo]
Sun 07:30 AM  Breakfast          Milo  daily   [todo]
Sun 08:00 AM  Morning walk       Rex   daily   [todo]
Sun 08:15 AM  Give meds          Milo  daily   [todo]
Sun 12:00 PM  Feather toy play   Milo  once    [todo]
Sun 05:30 PM  Brushing           Rex   weekly  [todo]
Sun 07:00 PM  Litter box clean   Milo  daily   [todo]

Only Milo's tasks (filter_tasks pet_name='Milo')
========================================
Sun 07:00 PM  Litter box clean   Milo  daily   [todo]
Sun 12:00 PM  Feather toy play   Milo  once    [todo]
Sun 08:15 AM  Give meds          Milo  daily   [todo]
Sun 07:30 AM  Breakfast          Milo  daily   [todo]

Conflict warnings for today (detect_conflicts)
========================================
WARNING: Rex's 'Breakfast' (07:30-07:40) is at the same time as Milo's 'Breakfast' (07:30-07:40)
WARNING: Rex's 'Morning walk' (08:00-08:30) overlaps Milo's 'Give meds' (08:15-08:20)

Today's Schedule (Sunday, October 18)
========================================
07:30 AM  Breakfast          Rex    10 min  [high]
07:30 AM  Breakfast          Milo   10 min  [high]
08:00 AM  Morning walk       Rex    30 min  [high]
08:15 AM  Give meds          Milo    5 min  [high]
12:00 PM  Feather toy play   Milo   20 min  [medium]
05:30 PM  Brushing           Rex    15 min  [low]

Plan for Jose: 6 task(s), 90 of 90 minutes used.
Tasks are picked by priority (high, then medium, then low); ties go to the earlier task.
- 07:30 Breakfast (Rex, high priority, 10 min): included, it fit in the remaining time.
- 07:30 Breakfast (Milo, high priority, 10 min): included, it fit in the remaining time.
- 08:00 Morning walk (Rex, high priority, 30 min): included, it fit in the remaining time.
- 08:15 Give meds (Milo, high priority, 5 min): included, it fit in the remaining time.
- 12:00 Feather toy play (Milo, medium priority, 20 min): included, it fit in the remaining time.
- 17:30 Brushing (Rex, low priority, 15 min): included, it fit in the remaining time.
- Skipped Litter box clean (Milo, medium priority, 45 min): needed 45 min but only 0 were left.
Warnings:
- Rex's 'Breakfast' (07:30-07:40) is at the same time as Milo's 'Breakfast' (07:30-07:40)
- Rex's 'Morning walk' (08:00-08:30) overlaps Milo's 'Give meds' (08:15-08:20)

Recurring tasks (mark_task_complete)
========================================
Completed Rex's 'Morning walk' due Sun 08:00 AM.
Next one was created automatically, due Mon 08:00 AM.
Completed Milo's 'Feather toy play' (once), so no next one was created.

Completed tasks (filter_tasks completed=True)
========================================
Sun 08:00 AM  Morning walk       Rex   daily   [done]
Sun 12:00 PM  Feather toy play   Milo  once    [done]

Rex's tasks still to do, sorted (filter + sort)
========================================
Sun 07:30 AM  Breakfast          Rex   daily   [todo]
Sun 05:30 PM  Brushing           Rex   weekly  [todo]
Mon 08:00 AM  Morning walk       Rex   daily   [todo]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```text
tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  4%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  9%]
tests/test_pawpal.py::test_sort_by_time_orders_tasks_added_out_of_order PASSED [ 13%]
tests/test_pawpal.py::test_sort_by_time_with_no_tasks_returns_empty_list PASSED [ 18%]
tests/test_pawpal.py::test_filter_by_pet_name_ignores_case PASSED        [ 22%]
tests/test_pawpal.py::test_filter_by_completion_status PASSED            [ 27%]
tests/test_pawpal.py::test_filter_by_pet_and_status_together PASSED      [ 31%]
tests/test_pawpal.py::test_filter_with_no_filters_returns_every_pets_tasks PASSED [ 36%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_copy PASSED [ 40%]
tests/test_pawpal.py::test_completing_weekly_task_creates_copy_seven_days_later PASSED [ 45%]
tests/test_pawpal.py::test_daily_task_rolls_over_to_next_month PASSED    [ 50%]
tests/test_pawpal.py::test_completing_once_task_does_not_create_copy PASSED [ 54%]
tests/test_pawpal.py::test_completing_same_task_twice_does_not_duplicate PASSED [ 59%]
tests/test_pawpal.py::test_completing_task_from_another_owner_raises_error PASSED [ 63%]
tests/test_pawpal.py::test_tasks_at_same_time_for_different_pets_conflict PASSED [ 68%]
tests/test_pawpal.py::test_overlapping_tasks_for_same_pet_conflict PASSED [ 72%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 77%]
tests/test_pawpal.py::test_completed_tasks_are_ignored_for_conflicts PASSED [ 81%]
tests/test_pawpal.py::test_conflicts_on_other_days_are_excluded_when_day_given PASSED [ 86%]
tests/test_pawpal.py::test_no_tasks_means_no_conflicts PASSED            [ 90%]
tests/test_pawpal.py::test_daily_plan_picks_high_priority_first_within_time_limit PASSED [ 95%]
tests/test_pawpal.py::test_daily_plan_skips_completed_tasks_and_other_days PASSED [100%]
============================= 22 passed in 0.04s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Earliest due time first, across all pets |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | By pet (any capitalization), by done/not done, or both |
| Conflict handling | `Scheduler.detect_conflicts(day)` | Warns about overlapping durations, not just exact matches; never crashes |
| Recurring tasks | `Scheduler.mark_task_complete(task)` | Daily → next day, weekly → 7 days later; "once" tasks don't repeat |
| Daily plan | `Scheduler.generate_daily_plan(day)`, `Scheduler.explain_plan(plan, day)` | Highest priority first, within the owner's available minutes |

**Sorting:** `sort_by_time()` uses Python's `sorted()` with a lambda key, `key=lambda task: task.due_time`. Because `due_time` is a `datetime`, tasks sort by date and then time. Tasks at the same time keep the order they were added.

**Filtering:** `filter_tasks()` keeps a task only if it matches every filter given. Leaving a filter as `None` means "don't filter on this." The Streamlit app uses it for the "Show pet" and "Show status" dropdowns.

**Conflict detection:** `detect_conflicts()` sorts the unfinished tasks by time, then checks every pair with `itertools.combinations`. Two tasks clash if the later one starts before the earlier one ends (`due_time + duration_minutes`). It returns warning strings instead of raising errors. Exact matches say "is at the same time as", partial overlaps say "overlaps", and back-to-back tasks (8:00–8:30, then 8:30) don't count. It works for the same pet or different pets, and passing a `day` limits it to that day.

**Recurring tasks:** `mark_task_complete()` marks the task done. If its frequency is `daily` or `weekly`, it adds a new copy to the same pet, due `timedelta(days=1)` or `timedelta(weeks=1)` after the original due time, so it rolls over months and years correctly. Completing the same task twice doesn't create duplicates. The Streamlit app's "Mark done" button calls this method.

**Daily plan:** `generate_daily_plan()` skips completed tasks and tasks on other days. It picks tasks in priority order (ties go to the earlier task) while they fit in the owner's available minutes, then returns them in time order. `explain_plan()` says why each task was included or skipped and lists any conflicts.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
