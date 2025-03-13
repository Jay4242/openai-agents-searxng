import pytest
from examples.tools.searxng_search import searxng_search
from agents import RunContextWrapper
from typing import Any
import logging
import os
import asyncio

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_searxng_search(capfd, monkeypatch):
    """Tests the searxng_search tool with a basic query and captures output."""
    logger.info("Starting test_searxng_search")
    # Disable tracing using monkeypatch
    monkeypatch.setenv("OPENAI_AGENTS_DISABLE_TRACING", "")
    logger.info("Tracing disabled (or attempted to be)")

    # Set the SEARXNG_BASE_URL environment variable for the test
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://searx.lan")

    query = "What is the capital of France?"
    logger.info(f"Query set to: {query}")
    ctx = RunContextWrapper[Any](context=None)  # type: ignore
    logger.info("RunContextWrapper created")
    try:
        # Remove whitespaces from the query
        query = query.replace(" ", "+")
        result = await searxng_search(ctx, query)
        if capfd:
            logger.info("capfd is not None")
            captured = capfd.readouterr()
        else:
            logger.info("capfd is None, skipping readouterr")
        assert isinstance(result, list)
        assert len(result) > 0
        logger.info("Assertions passed")
    except Exception as e:
        logger.exception(f"Exception occurred during test: {e}")
        raise
    finally:
        logger.info("Ending test_searxng_search")

if __name__ == "__main__":
    async def run_test():
        # Create a pytest.MonkeyPatch instance
        mp = pytest.MonkeyPatch()
        try:
            await test_searxng_search(capfd=None, monkeypatch=mp)
        finally:
            mp.undo()  # Ensure monkeypatch is undone after the test

    asyncio.run(run_test())
