from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "A pet care planner for busy owners. Add your pets and their care tasks, "
    "and PawPal+ builds today's plan around the time you have."
)

with st.expander("How it works"):
    st.markdown(
        """
1. Enter your name and how many minutes you have for pet care today.
2. Add your pets, then give each one tasks with a time, duration, priority, and how often it repeats.
3. Filter and sort your tasks, and mark them done. Daily and weekly tasks automatically get their next one added.
4. Generate today's schedule. PawPal+ picks the highest-priority tasks that fit your time,
   warns you about overlapping tasks, and explains its choices.
"""
    )


def show_conflicts(conflicts: list[str]) -> None:
    """Show all time conflicts as one warning with a tip on how to fix them."""
    if not conflicts:
        return
    count = len(conflicts)
    lines = "\n".join(f"- {conflict}" for conflict in conflicts)
    st.warning(
        f"**⚠️ {count} time conflict{'s' if count != 1 else ''} today**\n\n"
        f"{lines}\n\n"
        "Tip: you can't be in two places at once. Move one task to a different "
        "time, or mark one done if it's already handled."
    )


st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Minutes available today", min_value=1, max_value=1440, value=90
)

# The Owner is the single source of truth for pets and tasks. Create it only
# once so it survives Streamlit's rerun on every interaction.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes=int(available_minutes))
owner = st.session_state.owner
owner.name = owner_name
owner.available_minutes = int(available_minutes)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        name = new_pet_name.strip()
        if not name:
            st.error("Please enter a pet name.")
        elif any(pet.name.lower() == name.lower() for pet in owner.pets):
            st.error(f"{owner.name} already has a pet named {name}.")
        else:
            owner.add_pet(Pet(name, species))
            st.success(f"Added {name}.")

st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        pet_index = st.selectbox(
            "Pet",
            range(len(owner.pets)),
            format_func=lambda i: f"{owner.pets[i].name} ({owner.pets[i].species})",
        )
        description = st.text_input("Task description", value="Morning walk")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            due = st.time_input("Due time", value=time(8, 0))
        with col2:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col4:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            if not description.strip():
                st.error("Please enter a task description.")
            else:
                pet = owner.pets[pet_index]
                pet.add_task(
                    Task(
                        description.strip(),
                        datetime.combine(date.today(), due),
                        int(duration),
                        priority,
                        frequency,
                    )
                )
                st.success(f"Added '{description.strip()}' for {pet.name}.")

scheduler = Scheduler(owner)
today = date.today()

st.subheader("Pets")
if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    st.table(
        [
            {"pet": pet.name, "species": pet.species, "tasks": len(pet.get_tasks())}
            for pet in owner.pets
        ]
    )

st.subheader("Tasks")
if not owner.get_all_tasks():
    st.info("No tasks yet. Add one above.")
else:
    # Mark a task done. Daily/weekly tasks get their next occurrence added.
    pending = sorted(scheduler.filter_tasks(completed=False), key=lambda t: t.due_time)
    if pending:
        col1, col2 = st.columns([3, 1])
        with col1:
            to_complete = st.selectbox(
                "Mark a task done",
                range(len(pending)),
                format_func=lambda i: (
                    f"{pending[i].due_time:%a %H:%M} - {pending[i].pet_name}: "
                    f"{pending[i].description}"
                ),
            )
        with col2:
            st.write("")  # line the button up with the dropdown
            if st.button("Mark done"):
                task = pending[to_complete]
                next_task = scheduler.mark_task_complete(task)
                if next_task:
                    st.success(
                        f"Done! Next '{next_task.description}' for {next_task.pet_name} "
                        f"added for {next_task.due_time:%a %b %d at %H:%M} ({task.frequency})."
                    )
                else:
                    st.success(f"Done! '{task.description}' doesn't repeat.")

    # Filter with Scheduler.filter_tasks(), then sort by time.
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [pet.name for pet in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["To do", "Done", "All"])
    shown = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"To do": False, "Done": True, "All": None}[status_filter],
    )
    shown = sorted(shown, key=lambda t: t.due_time)
    if shown:
        st.table(
            [
                {
                    "when": f"{task.due_time:%a %H:%M}",
                    "pet": task.pet_name,
                    "task": task.description,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                    "repeats": task.frequency,
                    "done": "yes" if task.completed else "no",
                }
                for task in shown
            ]
        )
    else:
        st.caption("No tasks match these filters.")

    show_conflicts(scheduler.detect_conflicts(today))

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Picks the highest-priority tasks for today that fit in your available minutes."
)

if st.button("Generate schedule"):
    plan = scheduler.generate_daily_plan(today)
    if plan:
        used = sum(task.duration_minutes for task in plan)
        st.success(
            f"Today's plan: {len(plan)} task(s), "
            f"{used} of {owner.available_minutes} minutes used."
        )
        st.table(
            [
                {
                    "time": f"{task.due_time:%H:%M}",
                    "pet": task.pet_name,
                    "task": task.description,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                }
                for task in plan
            ]
        )
    else:
        st.warning("No tasks fit today's plan. Add tasks or increase your available minutes.")

    planned = {id(task) for task in plan}
    skipped = [
        task
        for task in scheduler.filter_tasks(completed=False)
        if task.due_time.date() == today and id(task) not in planned
    ]
    if skipped:
        st.info(
            "**Didn't fit today:** "
            + ", ".join(
                f"{task.description} ({task.pet_name}, {task.duration_minutes} min)"
                for task in sorted(skipped, key=lambda t: t.due_time)
            )
            + ". Add more minutes to fit them in."
        )
    show_conflicts(scheduler.detect_conflicts(today))

    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan(plan, today))
