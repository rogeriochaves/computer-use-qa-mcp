import asyncio
import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional, Literal, cast
from mcp.server.fastmcp import FastMCP

from computer_use_qa_mcp.tools import BashTool, ComputerTool, EditTool, ToolResult
from computer_use_qa_mcp.loop import sampling_loop, APIProvider
from computer_use_qa_mcp.tools import ToolResult
from computer_use_qa_mcp.tools.overlay import get_overlay, cleanup_overlay
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

# Initialize overlay
overlay = get_overlay()


def format_tool_action(tool_name: str, tool_input: dict) -> str:
    """
    Format tool actions for display in the overlay.

    Args:
        tool_name: Name of the tool being executed
        tool_input: Input parameters for the tool

    Returns:
        Formatted action string for overlay display
    """
    if tool_name == "bash":
        command = tool_input.get("command", "")
        return f"$ {command}"

    elif tool_name == "computer":
        action = tool_input.get("action", "")
        text = tool_input.get("text", "")
        coordinate = tool_input.get("coordinate", [])

        if action == "mouse_move":
            if coordinate:
                return f"mouse_move ({coordinate[0]}, {coordinate[1]})"
            return "mouse_move"
        elif action == "left_click":
            return "click"
        elif action == "right_click":
            return "right click"
        elif action == "double_click":
            return "double click"
        elif action == "type":
            return f'type "{text}"'
        elif action == "key":
            # Handle special key mappings
            key_mappings = {
                "Return": "enter ⏎",
                "return": "enter ⏎",
                "enter": "enter ⏎",
                "Tab": "tab ⇥",
                "tab": "tab ⇥",
                "Escape": "esc",
                "esc": "esc",
                "Space": "space",
                "space": "space",
            }
            formatted_key = key_mappings.get(
                text, text if text.startswith("f") else text.lower()
            )
            return formatted_key
        elif action == "screenshot":
            return "📸 screenshot"
        else:
            return f"{action}" + (f" {text}" if text else "")

    elif tool_name == "str_replace_editor":
        command = tool_input.get("command", "")
        path = tool_input.get("path", "")

        if command == "view":
            return f"📖 view {path}"
        elif command == "create":
            return f"📝 create {path}"
        elif command == "str_replace":
            return f"✏️ edit {path}"
        elif command == "insert":
            return f"➕ insert in {path}"
        elif command == "undo_edit":
            return f"↩️ undo {path}"
        else:
            return f"edit: {command} {path}"

    # Fallback for unknown tools
    return f"{tool_name}: {str(tool_input)[:50]}..."


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

    def tool_action_callback(tool_uses: list[tuple[str, dict]]):
        """Handle overlay display for tool actions."""
        if not tool_uses:
            return

        # Format all actions and concatenate with newlines
        formatted_actions = []
        for tool_name, tool_input in tool_uses:
            formatted_action = format_tool_action(tool_name, tool_input)
            formatted_actions.append(formatted_action)

        # Show concatenated actions in overlay
        combined_action = "\n".join(formatted_actions)

        # Show overlay for all actions - only hide during actual execution in computer tool
        overlay.show_action(combined_action, duration=1.0)

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

    try:
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
            tool_action_callback=tool_action_callback,
        )
    finally:
        # Hide overlay after sampling loop completes
        overlay.hide()

    last_message = messages[-1]

    if not last_message:
        return "No response from the QA agent"

    if not isinstance(last_message["content"], str):
        if isinstance(last_message["content"], list) and len(last_message["content"]) > 0 and last_message["content"][0].type == "text": # type: ignore
            return last_message["content"][0].text # type: ignore
        else:
            return str(last_message["content"])

    return last_message["content"]


def main():
    """Main entry point for the MCP server."""
    logger.info("MCP server started")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
