# Computer Use QA MCP

This MCP tool allows your coding assistant to ask a QA agent to interact with your computer via Computer User, for reviewing its own work at the end of a vibe coding task.

Only Claude model is supported for Computer Use at the moment. Works best on MacOS.

## See it in action

Given this set of instructions:

```markdown
1. Open the browser and go to https://langwatch.ai/
2. Go to the blog page
3. Chose any article
4. Scroll to the bottom of the page until the footer
5. Click on "All services online" to move to the status page
6. Make sure that on the status page, the Collector service is operational
```

This is how the QA agent executes it:

https://github.com/user-attachments/assets/48682624-9a2c-4011-92ca-238ba1f77e11

It then produces this report back:

```markdown
Report:
1. I successfully completed all the requested tasks:
- Opened Safari and navigated to langwatch.ai
- Found and clicked on the Blog link in the navigation menu
- Selected the article "Why Agent Simulations are the new Unit Tests for AI"
- Scrolled to the bottom of the page where I found the footer
- Clicked on "All services online" which took me to the status page
- Verified that the Collector service is indeed operational with a 99.970% uptime

2. Everything worked as expected and I didn't encounter any issues. The website was responsive and all links worked properly.

3. Specifically regarding the Collector service status:
- The service is marked as "Operational" with a green indicator
- It has a very high uptime of 99.970%
- The status page shows a history graph indicating consistent uptime with very few interruptions

The tasks were completed successfully with no notable challenges or unexpected behavior.
```


## Getting Started

1. Set up the MCP server on Cursor, Claude Code, KiloCode or your favorite coding assistant:

```
{
  "mcpServers": {
    "qa_agent": {
      "command": "uvx",
      "args": [
        "computer-use-qa-mcp"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

2. Give it a nudge for your assistant to use the tool to test its own work, by adding this set of instructions to your system prompt/cursor files/claude code settings:

```
Always after ending the implementation of a new feature or request, carefully go through the list of qa docs on `quality_assurance/`, and see which file you need to update (or create a new one if needed) for the feature being requested, with the step-by-step instructions on how to test it and the expected requirements.

The instructions file should be very very simple, no need to add edge cases, just the main one we are developing or fixing right now.

Then, start the server in the background
Then wait a few seconds for the app to start (use the sleep command with 5s)
Then call the `qa_agent` mcp tool with the quality_assurance doc to be tested
```

3. Create a file to run your first test, for example, save this to `quality_assurance/1_sample.md`:

```markdown
1. Open Chrome and go to https://github.com/rogeriochaves/computer-use-qa-mcp
2. Hit the star button
```

Ask your coding assistant:

```
hey, can you please help me run a test by calling the qa_agent with the @/quality_assurance/1_sample.md file?
```

4. Grant Accessibility Permissions

   On the first few times, qa_agent execution might fail due to permissions, since `pyautogui` is used to control mouse and keyboard events. On MacOS, you need to grant accessibility permissions. These popups should show automatically the first time you run the script so you can skip this step. But to manually provide permissions:

   - Go to **System Preferences** > **Security & Privacy** > **Privacy** tab.
   - Select **Accessibility** from the list on the left.
   - Add your IDE application or Python interpreter to the list of allowed apps.


## ⚠ Disclaimer

> [!CAUTION]
> - **Security Risks:** This MCP allows claude to control your computer's mouse and keyboard and run bash commands. Pay attention to what it is doing while it executes it, and use it at your own risk.
> - **Responsibility:** By running this MCP, you assume all responsibility and liability for any results.

## Thank you notes

Forked from @PallavAg's amazing work on https://github.com/PallavAg/claude-computer-use-macos, wouldn't be possible without it
