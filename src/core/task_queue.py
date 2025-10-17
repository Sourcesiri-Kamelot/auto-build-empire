# --- AUTONOMOUS ENTERPRISE BUILDER - TASK QUEUE v1.0 ---
# This is the central message bus for the entire swarm. It is the digital
# "assembly line" where micro-tasks are placed, prioritized, and claimed
# by specialized agents. It is engineered to be simple, robust, and
# handle thousands of concurrent operations.

import queue
import time
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class Task:
    """A single, atomic unit of work for the swarm."""
    priority: int
    task_id: str = field(compare=False)
    name: str = field(compare=False)
    data: Any = field(compare=False)
    required_skills: list[str] = field(default_factory=list, compare=False)
    status: str = "PENDING"
    created_at: float = field(default_factory=time.time, compare=False)

class TaskQueue:
    def __init__(self):
        # A priority queue ensures that the most critical tasks
        # (e.g., refinements from the QA loop) are handled first.
        self.queue = queue.PriorityQueue()
        self.task_counter = 0
        print("[TaskQueue] Assembly Line is online.")

    def add_task(self, name: str, data: Any, required_skills: list[str], priority: int = 10):
        """Adds a new micro-task to the assembly line."""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:04d}"
        task = Task(priority=priority, task_id=task_id, name=name, data=data, required_skills=required_skills)
        self.queue.put(task)
        print(f"[TaskQueue] ADDED: {task_id} - {name} (Priority: {priority}, Skills: {required_skills})")
        return task_id

    def claim_task(self, agent_skills: list[str]) -> Task | None:
        """
        Called by a worker agent. It attempts to claim a task that matches
        its skill set. This is a simplified claiming mechanism. A production
        system might involve more complex locking.
        """
        if not self.queue.empty():
            task = self.queue.get()
            # SKILL MATCHING IMPLEMENTED - Critical fix from QA audit
            if any(skill in agent_skills for skill in task.required_skills):
                task.status = "CLAIMED"
                print(f"[TaskQueue] CLAIMED: {task.task_id} by agent with skills {agent_skills}")
                return task
            else:
                # Put task back if skills don't match
                self.queue.put(task)
                return None
        return None

    def complete_task(self, task: Task):
        """Marks a task as complete."""
        task.status = "COMPLETED"
        print(f"[TaskQueue] COMPLETED: {task.task_id}")
        # In a real system, this would trigger logging and result storage.
        self.queue.task_done()
