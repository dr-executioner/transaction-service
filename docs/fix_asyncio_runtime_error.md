# Fix: `RuntimeError: no running event loop` and `AttributeError: 'NoneType' object has no attribute 'send'`

## Issue Description

When processing a second transaction via the `/webhook/transactions` endpoint after a server restart, the application encountered a `RuntimeError: no running event loop`. This error occurred because `asyncio.run()` was being called within a Celery worker, which might already have an active event loop or manage asynchronous tasks in a way that conflicts with `asyncio.run()`'s default behavior of creating a new event loop. The subsequent `AttributeError: 'NoneType' object has no attribute 'send'` was a symptom of the underlying event loop issue, likely due to a corrupted or improperly closed database connection.

The traceback indicated the problem originated in `app/utils/helper.py` within the `run_async` function, which is used by `app/services/transaction_service.py`'s `process_transaction_task`.

## Root Cause

The `asyncio.run()` function is designed to be the main entry point for an asynchronous application and expects to be run in a context where no other event loop is currently running. When `process_transaction_task` (a synchronous Celery task) calls `run_async`, it attempts to execute an async function (`process_transaction`). The `run_async` helper tries to get a running loop and, if none exists, calls `asyncio.run()`. On the second transaction, it's likely that a loop *was* already running (perhaps from a previous task execution or Celery's internal mechanisms), leading to the `RuntimeError`.

## Solution

To resolve this, the `nest_asyncio` library was used. `nest_asyncio` patches `asyncio` to allow `asyncio.run()` to be called when an event loop is already running in the current thread. This enables seamless execution of asynchronous code within environments that might already have an active event loop, such as Celery workers.

### Steps Taken:

1.  **Identified the Problem:** Analyzed the traceback, specifically the `RuntimeError: no running event loop` and its origin in `app/utils/helper.py` and `app/services/transaction_service.py`.
2.  **Researched Solution:** Determined that `nest_asyncio` is the appropriate tool for allowing nested `asyncio.run()` calls.
3.  **Installed `nest_asyncio`:** The user confirmed that `nest_asyncio` was installed in the project's environment.
4.  **Modified `app/utils/helper.py`:**
    *   Imported `nest_asyncio`.
    *   Applied `nest_asyncio.apply()` within the `run_async` function's `except RuntimeError` block. This ensures that if `asyncio.get_running_loop()` fails (meaning no loop is explicitly running, but one might be implicitly managed or about to be started), `nest_asyncio` prepares the environment for `asyncio.run()` to operate correctly without conflict.

### Code Changes in `app/utils/helper.py`:

```python
import asyncio
import nest_asyncio

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — create one
        nest_asyncio.apply() # Apply nest_asyncio to allow nested event loops
        return asyncio.run(coro)
    else:
        # Already in an async context — schedule it properly
        return loop.create_task(coro)
```

## Verification

After these changes, the application should be able to process multiple transactions without encountering the `RuntimeError` or `AttributeError`, as `nest_asyncio` will correctly manage the asynchronous event loop context.