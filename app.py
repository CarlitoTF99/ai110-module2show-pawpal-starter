from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
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
        col1, col2, col3 = st.columns(3)
        with col1:
            due = st.time_input("Due time", value=time(8, 0))
        with col2:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
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
                    )
                )
                st.success(f"Added '{description.strip()}' for {pet.name}.")

st.subheader("Current pets and tasks")
if not owner.pets:
    st.info("No pets yet. Add one above.")
for pet in owner.pets:
    st.markdown(f"**{pet.name}** ({pet.species})")
    tasks = pet.get_tasks()
    if tasks:
        st.table(
            [
                {
                    "time": f"{task.due_time:%H:%M}",
                    "task": task.description,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                    "done": task.completed,
                }
                for task in tasks
            ]
        )
    else:
        st.caption("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Picks the highest-priority tasks for today that fit in your available minutes."
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(date.today())
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
    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan(plan, date.today()))
