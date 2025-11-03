import asyncio

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        raise RuntimeError("Already running inside event loop, cannot run async here directly")
    except RuntimeError:
       return asyncio.run(coro)
