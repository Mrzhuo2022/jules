import os

# --- JWT Settings ---
# It's critical that this is loaded from an environment variable in production.
# A fixed secret is a security risk.
SECRET_KEY = os.environ.get("SECRET_KEY", "a_very_secret_key_for_dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- Database Settings ---
# This should also be configured via environment variables for production.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/subtracker")
