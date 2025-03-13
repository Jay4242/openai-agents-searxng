# SearxNG Search Tool

This tool allows agents to search the web using a self-hosted [SearxNG](https://searxng.org/) instance. It's designed to integrate SearxNG into agent workflows.

## Overview

The `searxng_search` tool is a `FunctionTool` that takes a search query as input and returns a list of search results. Each result includes the title, URL, and content of the search result.

## Usage

To use this tool, you need a running SearxNG instance accessible from your network. By default, the tool assumes that your SearxNG instance is available at `http://searx.lan`.

### Configuration

You can configure the base URL of your SearxNG instance by setting the `SEARXNG_BASE_URL` environment variable. If this variable is not set, the tool will default to `http://searx.lan`.

```bash
export SEARXNG_BASE_URL="http://your-searxng-instance.lan"
```

### Example

Here's a simplified example of how to use the `searxng_search` tool in an agent:

```python
import os
from agents import Agent, FunctionTool, RunContextWrapper, Runner
from typing import Any
from examples.tools.searxng_search import searxng_search, searxng_tool  # Import the searxng_search function and searxng_tool

SEARXNG_BASE_URL = os.environ.get("SEARXNG_BASE_URL", "http://searx.lan")

# Create an agent with the searxng_tool
agent = Agent(
    name="SearxNG Search Agent",
    instructions="Use the searxng_search tool to answer user questions.",
    tools=[searxng_tool],
)

# Example usage (this would typically be part of an async main function)
async def main():
    result = await Runner.run(agent, "What is the capital of France?")
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Dependencies

*   `beautifulsoup4`
*   `requests` (implicitly, via the `curl` command)

### Notes

*   The tool uses `curl` to make HTTP requests. Ensure that `curl` is installed on your system and available in your system's PATH.
*   The tool mimics the user agent string and URL construction of a web browser.
*   Error handling is included, but you may want to add more robust error handling for production use.
*   Consider sanitizing the `query` input to prevent command injection vulnerabilities.
*   The tool extracts text content from HTML using BeautifulSoup. This may not be suitable for all websites.

### Testing

To run the tests, execute the following command:

```bash
pytest tests/test_searxng_search.py
```
