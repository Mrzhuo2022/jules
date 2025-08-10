import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.api.v1 import auth, subscriptions
from src.services.reminder_service import check_for_reminders
from src.core.logging_config import setup_logging

# Configure logging
setup_logging()

# Setup the scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, add the job to the scheduler
    # For testing, we run it every 15 seconds. In production, this would be 'cron' and run daily.
    scheduler.add_job(check_for_reminders, 'interval', seconds=15)
    scheduler.start()
    logging.info("Scheduler started...")
    yield
    # On shutdown, stop the scheduler
    scheduler.shutdown()
    logging.info("Scheduler shut down.")


# Initialize the FastAPI app with the lifespan manager
app = FastAPI(
    title="SubTracker API",
    description="API for managing personal subscriptions and renewal reminders.",
    version="1.0.0",
    lifespan=lifespan
)

# Include the API routers
# The `prefix` adds a path prefix to all routes in the router.
# The `tags` are used for grouping endpoints in the API docs.
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])

@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the SubTracker API!"}
