import asyncio
import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional, Literal, cast
from mcp.server.fastmcp import FastMCP

from computer_use_demo.tools import BashTool, ComputerTool, EditTool, ToolResult
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolResult
from anthropic.types.beta import BetaMessage, BetaMessageParam
from anthropic import APIResponse

# Import the type definitions
Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
]

Command = Literal[
    "view",
    "create",
    "str_replace",
    "insert",
    "undo_edit",
]

# Initialize FastMCP server
mcp = FastMCP("computer-use")

# Set up logging to stderr (not stdout for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize tools
computer_tool = ComputerTool()
bash_tool = BashTool()
edit_tool = EditTool()


@mcp.tool()
async def run_quality_assurance(instructions_absolute_file_path: str) -> str:
    """
    This tool runs a quality assurance agent that and see and interact with the user screen to test the
    application.

    Given a file path to a file containing detailed step by step instructions on how to open the application,
    navigate to the correct page, and test what is needed to be done, plus what's expected on the behaviour,
    this tool will return a report from the QA agent of observations it found or issues that prevented it
    from progressing.

    Use this tool every time after finishing a new feature or bug fix to ensure the application is working as expected.

    Args:
        instructions_absolute_file_path: The absolute path to the file containing the instructions for the QA agent.

    Returns:
        A natural language report from the QA agent of observations it found or issues that prevented it from progressing.
    """

    file_content = open(instructions_absolute_file_path, "r").read()

    messages: list[BetaMessageParam] = [
        {
            "role": "user",
            "content": file_content,
        }
    ]

    def output_callback(content_block):
        if isinstance(content_block, dict) and content_block.get("type") == "text":
            logger.info("Assistant:" + content_block.get("text", ""))

    def tool_output_callback(result: ToolResult, tool_use_id: str):
        if result.output:
            logger.info(f"> Tool Output [{tool_use_id}]:\n{result.output}")
        if result.error:
            logger.error(f"!!! Tool Error [{tool_use_id}]:\n{result.error}")
        if result.base64_image:
            # Save the image to a file if needed
            os.makedirs("screenshots", exist_ok=True)
            image_data = result.base64_image
            with open(f"screenshots/screenshot_{tool_use_id}.png", "wb") as f:
                f.write(base64.b64decode(image_data))
            logger.info(f"Took screenshot screenshot_{tool_use_id}.png")

    def api_response_callback(response: APIResponse[BetaMessage]):
        logger.info(
            "\n---------------\nAPI Response:\n"
            + json.dumps(json.loads(response.text)["content"], indent=4)  # type: ignore
            + "\n",
        )

    messages = await sampling_loop(
        model="claude-3-5-sonnet-20241022",
        provider=APIProvider.ANTHROPIC,
        system_prompt_suffix="",
        messages=messages,
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        api_response_callback=api_response_callback,
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        only_n_most_recent_images=10,
        max_tokens=4096,
    )

    last_message = messages[-1]

    if not last_message:
        return "No response from the QA agent"

    if not isinstance(last_message["content"], str):
        if isinstance(last_message["content"], list) and len(last_message["content"]) > 0 and last_message["content"][0].type == "text": # type: ignore
            return last_message["content"][0].text # type: ignore
        else:
            return str(last_message["content"])

    return last_message["content"]


if __name__ == "__main__":
    # Run the MCP server
    logger.info("MCP server started")
    mcp.run(transport="stdio")
    # asyncio.run(run_quality_assurance("examples/langwatch_blog.md"))
