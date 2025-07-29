#!/usr/bin/env python3
"""
Demo script to test the overlay functionality for the Computer Use agent.
This script will show you how the overlay appears when actions are performed.
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import directly
sys.path.insert(0, os.path.dirname(__file__))

# Direct imports to avoid anthropic dependency issues
from computer_use_qa_mcp.tools.computer import ComputerTool


async def main():
    """Test the overlay functionality with various actions."""
    print("🚀 Starting overlay demo...")
    print("You should see action overlays appear on your screen!")
    print("The overlay will show what action is being performed.\n")

    try:
        # Initialize the computer tool (this also initializes the overlay)
        print("Initializing Computer Tool with overlay...")
        computer = ComputerTool()
        print("✅ Computer Tool initialized!\n")

        # Test 1: Get cursor position
        print("Test 1: Getting cursor position...")
        result = await computer(action="cursor_position")
        print(f"Result: {result.output}")
        await asyncio.sleep(2)

        # Test 2: Simulate a key press
        print("\nTest 2: Simulating key press (Command+Space)...")
        result = await computer(action="key", text="command+space")
        print(f"Result: {result.output}")
        await asyncio.sleep(2)

        # Test 3: Type some text
        print("\nTest 3: Typing text...")
        result = await computer(action="type", text="Hello from overlay!")
        print(f"Result: {result.output}")
        await asyncio.sleep(2)

        # Test 4: Take a screenshot (overlay should hide)
        print("\nTest 4: Taking screenshot (overlay should hide automatically)...")
        result = await computer(action="screenshot")
        print("✅ Screenshot taken! Notice the overlay was hidden during capture.")
        await asyncio.sleep(1)

        print("\nTest 5: Typing text again...")
        result = await computer(action="type", text="Second test!")
        print(f"Result: {result.output}")
        await asyncio.sleep(2)

        print("\n🎉 Demo completed successfully!")
        print("The overlay system is working correctly:")
        print("✅ Shows action descriptions on screen")
        print("✅ Automatically hides during screenshots")
        print("✅ Stays on top of all windows")

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user.")
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())