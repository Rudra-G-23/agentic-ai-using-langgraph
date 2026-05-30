import os
import sys

from loguru import logger
from rich.traceback import install

# 1. Detect if we are in Production
# (Set PRODUCTION=True in your production .env or environment variables)
IS_PRODUCTION = os.getenv("PRODUCTION", "False").lower() in ("true", "1", "yes")

# 2. Clear Loguru's default handler so we can customize it
logger.remove()

if IS_PRODUCTION:
    # PRODUCTION SETTING: Log to stdout as structured JSON for Datadog/ELK
    logger.add(sys.stdout, serialize=True, level="INFO")

    # Optional: Also log to a physical file
    logger.add("logs/production.log", rotation="10 MB", serialize=True, level="ERROR")

else:
    # DEVELOPMENT SETTING: Enable Rich for gorgeous local debugging
    install(show_locals=True)  # Hooks into standard Python exceptions

    # Tell Loguru to pass its logs through Rich's color formatter
    logger.add(sys.stdout, diagnose=True, backtrace=True, colorize=True, level="DEBUG")


# --- Example Usage in your LangChain / Ollama Code ---


def main():
    logger.info("Starting the LLM application...")

    try:
        # Simulating your Ollama connection
        logger.debug("Connecting to Ollama API...")
        raise ConnectionError(
            "Could not reach http://localhost:11434"
        )  # Simulated error

    except Exception:
        # Loguru catches the exception with full context
        logger.exception("Failed to connect to the Ollama API.")


if __name__ == "__main__":
    main()
