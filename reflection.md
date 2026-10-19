# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    - My UML design has four classes: Owner, Pet, Task, and Scheduler: an Owner has one or more Pets, each Pet has its own list of Tasks, and the Scheduler works with the Owner so it can get to all the tasks across every pet.
     
- What classes did you include, and what responsibilities did you assign to each?
     -  Owner: Holds the owner’s name, how many minutes they have available for pet care that day, and their list of pets. It can add a pet and pull together all the tasks from every pet it owns.

     - Pet: Stores the pet’s name, species, and its list of tasks. It’s responsible for adding tasks and returning them.

     - Task: Represents one care activity, like a walk, feeding, or meds. It has a description, due time, how long it takes, a priority, and whether it’s done. It can mark itself as complete.

     - Scheduler: This is where the logic happens. It doesn’t store tasks itself. Instead it uses the Owner to get every task, then sorts them by time, filters them by pet or completion status, checks for scheduling conflicts, and builds a daily plan that fits the owner’s available time based on priority..

**b. Design changes**

- Did your design change during implementation?
    - Yes, my design changed. My first draft had too many attributes and methods, and a lot of them felt redundant or more than I actually needed for the requirements. I decided to simplify it so each class only keeps what it really needs.
- If yes, describe at least one change and why you made it.
    - Owner: I removed preferences and the extra methods like remove_pet() and get_pet(). I kept available_minutes because the scheduler needs it to know how much time the owner has in a day.
    - Pet: I removed age and the extra task methods like remove_task() and get_pending_tasks(). Just add_task() and get_tasks() are enough to manage a pet’s tasks.
    - Task: I removed frequency, pet_name, and helper methods like priority_rank(), end_time(), overlaps_with(), and next_occurrence(). The task really only needs a description, due time, duration, priority, completion status, and mark_complete().
    - Later, some of this came back for good reasons. The assignment needed `frequency` for recurring tasks, and `pet_name` let the Scheduler get everything through `Owner.get_all_tasks()` and still know which pet each task belongs to. Instead of putting helpers like `end_time()` back on Task, I kept them as private helpers in the Scheduler. I also added `Scheduler.mark_task_complete()`, which creates the next copy of a daily or weekly task. A Task doesn't know its Pet, so it can't add its own copy, but the Scheduler can reach every pet through the Owner.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    - It looks at how many minutes the owner has that day, each task's priority (high, medium, low), and the task's due time. It skips tasks that are already done or aren't due today, and it warns me if two tasks overlap.
- How did you decide which constraints mattered most?
    - Time and priority mattered most, because a busy owner can't do everything, so the important stuff like meds and walks has to come first. Due time is used to break ties and to put the final plan in order.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - It picks tasks highest priority first and doesn't go back to rethink its choices. So a long medium-priority task can get skipped while a shorter low-priority one still fits. In my demo, "Litter box clean" (45 min) got skipped but "Brushing" (15 min) made it in.
- Why is that tradeoff reasonable for this scenario?
    - It's simple and easy to explain, and the high-priority tasks always get in first. For a handful of pet tasks a day, finding the perfect combination isn't worth the extra complexity.
- Another tradeoff: readability vs. speed in conflict detection.
    - My first `detect_conflicts()` used nested loops that stopped early once tasks couldn't overlap anymore. When I asked AI to simplify it, it suggested `itertools.combinations` to check every pair of tasks, plus moving the warning text into a helper. It also offered an even shorter one-line list comprehension.
    - I picked the `combinations` loop with the helper. It checks every pair instead of stopping early, so it's technically slower, but it's much easier to read. A pet owner only has a few dozen tasks a day, so the speed difference doesn't matter. I skipped the one-liner because it was harder to read and debug. All my tests still passed after the change, and it also checks overlapping durations, not just exact time matches.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - I used Claude Code as a coding assistant as suggested by the steps in the course portal. It fixed the syntax errors in my Mermaid UML diagram, turned the UML into Python class skeletons with dataclasses, reviewed the skeleton for missing relationships and slow spots, filled in the scheduling logic, wrote the `main.py` demo, and drafted my first pytest tests.
    - It also helped with debugging. When the tests couldn't import `pawpal_system`, it found that pytest wasn't looking in the project folder and added a `pytest.ini` to fix it.
- What kinds of prompts or questions were most helpful?
    - Prompts that included the assignment's exact requirements worked best. When I pasted in the step instructions (for example, that the Scheduler has to read tasks from an Owner method, not from a single pet), the AI caught that its own earlier code broke that rule and fixed it.
    - Follow-up questions that checked the AI's claims were also really helpful, like asking "every gap you found, is it fixed?"

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - When I asked the AI to review my skeleton, it said it had "fixed" several gaps. I asked whether every gap was really fixed, and it admitted most were only empty stubs with a plan in the docstring, and that two gaps hadn't been touched at all. After that I had it actually implement the methods.
    - The AI's first fix for my UML diagram still didn't render in my editor. I suspected the `~` characters it used for types like `list~Task~`, so I had it remove them, and then the diagram worked.
    - The AI first gave the Scheduler a helper that read `owner.pets` directly. When the assignment said the Scheduler must use the Owner's `get_all_tasks()` method, I had it change the design: each task now stores its `pet_name`, and the Scheduler only uses `get_all_tasks()`.
    - I had removed `frequency` and `pet_name` from Task in my design, but the assignment needed `frequency`, and `pet_name` made the change above possible. So I accepted adding them back, even though it reversed my earlier simplification.
- How did you evaluate or verify what the AI suggested?
    - I ran the code instead of trusting the AI's description. Running `main.py` exposed a misleading message: it said a task was skipped "after higher-priority tasks," even though a lower-priority task had been included. The real reason was that it didn't fit in the time left, so the message was changed to show the actual minutes.
    - I ran `pytest` to confirm the tests pass, and I checked the UML by rendering it, not just reading it.
    - I compared every change against the assignment instructions, especially the multi-pet requirement.

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?
    - Agent mode was the most useful, since it could edit several files at once. Adding recurring tasks meant changing `pawpal_system.py`, `main.py`, `app.py`, the tests and the UML together, and it kept them in sync.
    - It could also run things, not just write them: `python main.py`, `pytest`, rendering the Mermaid diagram, and even clicking through the Streamlit app in a test runner. That meant every change was checked right away.
    - Asking it to analyze first, check what was already done, and give me a plan before writing code helped a lot. Several Phase 4 features were already built, so it only did the parts that were actually missing.
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
    - When I asked the AI to simplify `detect_conflicts()`, it gave me three options. The shortest was a one-line list comprehension that was very "Pythonic" but hard to read. I rejected that one and kept the `combinations` loop with a separate `_conflict_message()` helper, because I want to be able to read and debug my own code.
    - Also, I wanted Task to stay simple, so for recurring tasks I chose to put the logic in the Scheduler (`mark_task_complete()`) instead of having the Task create copies of itself.
- How did using separate chat sessions for different phases help you stay organized?
    - Honestly, I mostly kept one long chat session instead of starting a new one for each phase. What kept me organized was working one phase at a time: I pasted in that phase's instructions, had the AI check what was already done, made a plan, and then went step by step. Next time I would start a new session for each phase, especially for testing, so the AI's context stays focused and it's easier to look back at what happened in each phase.
- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
    - The AI can write a lot of code quickly, but I'm the one who has to decide what the design should be and check that the result is actually right. It said gaps were "fixed" when they were only stubs, it wrote a test that passed even when the code was broken, and one of its messages explained a skipped task the wrong way. I only caught those by asking follow-up questions and running the code. Being the lead architect means setting the requirements, choosing between options, and verifying everything instead of just accepting it.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - I have 29 tests in `tests/test_pawpal.py`. They cover sorting (tasks added out of order come back in time order), filtering (by pet, by status, both, and a pet with no tasks), recurring tasks (daily goes to the next day, weekly goes 7 days later, Oct 31 rolls over to Nov 1, "once" doesn't repeat, no duplicates), conflict detection (exact same time, overlaps, back-to-back is not a conflict, completed tasks and other days are ignored), the daily plan, the plan explanation, and rejecting bad input like an invalid priority.
- Why were these tests important?
    - These are the parts that make the scheduler "smart," and they're easy to get slightly wrong without noticing, like off-by-one times or duplicate recurring tasks. To make sure the tests really work, I broke the code on purpose and checked that the right test failed. That showed one of my tests was weak: the priority test passed even when the plan ignored priority, because the high-priority task was also the earliest one. I fixed the test so only a priority-first plan passes.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    - 4 out of 5. All 29 tests pass, and they fail when I break the logic on purpose, so I trust the core scheduling. It's not a 5 because the Streamlit UI is only tested by hand, and the planner picks by priority first, so it doesn't always find the best combination of tasks.
- What edge cases would you test next if you had more time?
    - Tasks that go past midnight, a recurring task completed days late, an owner with 0 minutes or with a huge number of tasks, and two pets with the same name. I would also add automated tests for the Streamlit app using Streamlit's `AppTest`.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I'm most satisfied with how the classes work together. The Scheduler gets everything through `Owner.get_all_tasks()`, so adding a pet just works, and the same logic powers both `main.py` and the Streamlit app. I'm also happy with the tests, especially that I checked they actually catch bugs.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - I would make the planner smarter so it can fit more tasks in, for example trying smaller tasks first when a big one doesn't fit, or letting the owner set preferred times. I would also add editing and deleting tasks in the app, and save the data to a file so it doesn't disappear when the page is refreshed.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - Designing the classes first (the UML) made everything after it easier, because I knew where each piece of logic belonged. And with AI, the most important thing is to verify: run the code, run the tests, and ask "is this really done?" The AI is fast, but I'm responsible for making sure the result is correct and the design stays clean.
