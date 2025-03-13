from agents import FunctionTool, RunContextWrapper
from typing import Any
import subprocess
import json
import shlex
import re
import logging
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logger level to INFO

# Create a handler to print log messages to the console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create a formatter to format the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)


async def searxng_search(ctx: RunContextWrapper[Any], query: str) -> list[dict[str, str]]:
    """Searches the web using a SearxNG instance, mirroring the URL construction and HTML stripping from llm-websearch.bash using regex.

    Args:
        query: The search query.
    """
    logger.info(f"Starting searxng_search with query: {query}")
    base_url = "http://searx.lan"
    search_url = f"{base_url}/search"
    phrase = re.sub(r'\s+', '+', query)  # Replace spaces with plus signs
    url = f"{search_url}?q={phrase}&language=auto&time_range=&safesearch=0&categories=general"

    curl_command = f'curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36" "{url}"'

    logger.info(f"Executing curl command: {curl_command}")

    try:
        process = subprocess.Popen(
            curl_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("subprocess.Popen executed")
        stdout, stderr = process.communicate()
        logger.info("process.communicate() completed")
        return_code = process.returncode
        logger.info(f"Curl command return code: {return_code}")

        if stdout == b"":
            logger.warning("stdout is empty")

        if stderr == b"":
            logger.warning("stderr is empty")
        else:
            logger.info(f"stderr: {stderr.decode('utf-8')}")

        if return_code == 0:
            html_content = stdout.decode("utf-8")
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract text from the entire HTML
            text = soup.get_text(separator=' ', strip=True)
            logger.info(f"Text Content: {text}")

            results = []
            for result in soup.find_all('article', class_='result'):
                title_element = result.find('a', class_='url_header')
                title = title_element.text if title_element else "No Title"
                url = title_element['href'] if title_element and 'href' in title_element.attrs else "No URL"
                content_element = result.find('p', class_='content')
                content = content_element.text if content_element else "No Content"

                results.append({
                    'title': title.strip(),
                    'url': url.strip(),
                    'content': content.strip()
                })

            print(f"{results}")
            logger.info(f"Parsed Results: {results}")
            return results
        else:
            error_message = stderr.decode('utf-8')
            logger.error(f"Error executing curl command: {error_message}")
            logger.info(f"Returning error message: An unexpected error occurred: {error_message}")
            return [{"error": f"Error executing curl command: {error_message}"}]
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        logger.info(f"Returning error message: An unexpected error occurred: {e}")
        return [{"error": f"An unexpected error occurred: {e}"}]
    finally:
        logger.info("Ending searxng_search")


searxng_tool = FunctionTool(
    name="searxng_search",
    description="Searches the web using a SearxNG instance, mirroring the URL construction and HTML stripping from llm-websearch.bash using regex.",
    params_json_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to use."
            }
        },
        "required": ["query"],
    },
    on_invoke_tool=searxng_search,
)
