import asyncio
import nest_asyncio

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — create one
        nest_asyncio.apply()
        return asyncio.run(coro)
    else:
        # Already in an async context — schedule it properly
        return loop.create_task(coro)
