#!/usr/bin/env python3
"""
Redis Streams Task Queue - Enterprise Scale Implementation
Production-tested pattern for 140+ agent coordination
"""
import redis
import json
import os
from dataclasses import asdict
from ..core.task import Task

# Production Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

TASK_STREAM = "agent_task_stream"
AGENT_GROUP = "worker_agents"

# Initialize stream and consumer group
try:
    redis_client.xgroup_create(TASK_STREAM, AGENT_GROUP, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "already exists" not in str(e):
        raise

def add_task(task: Task) -> str:
    """Add task to Redis stream"""
    task_payload = asdict(task)
    task_id = redis_client.xadd(TASK_STREAM, {"task_data": json.dumps(task_payload)})
    return task_id

async def claim_and_process_task(agent_id: str, agent_skills: list, execute_callback):
    """Main async loop for agent task processing"""
    while True:
        response = redis_client.xreadgroup(
            groupname=AGENT_GROUP,
            consumername=agent_id,
            streams={TASK_STREAM: ">"},
            count=1,
            block=2000
        )

        if not response:
            continue

        stream, messages = response[0]
        message_id, task_data = messages[0]
        task = json.loads(task_data['task_data'])

        if any(skill in agent_skills for skill in task.get('required_skills', [])):
            result = await execute_callback(task)
            redis_client.xack(TASK_STREAM, AGENT_GROUP, message_id)
