import asyncio

# Global asyncio queue is used as an in-memory trigger, but tasks persist in DB.
# The worker loop polls DB for 'queued' tasks as well.

queue = asyncio.Queue()

async def notify_new_task(task_id: int):
    await queue.put(task_id)

async def wait_for_task_id():
    task_id = await queue.get()
    queue.task_done()
    return task_id
