import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import anthropic
from config import MODEL
from tools import handle_tool_call


def run_agent(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_message: str,
    tools: list,
    max_turns: int = 30,
    verbose: bool = True,
    agent_name: str = "Agent",
) -> str:
    """Run a tool-use agent loop until it produces a final text response."""
    messages = [{"role": "user", "content": user_message}]

    for turn in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    if verbose:
                        print(f"[{agent_name}] Done after {turn + 1} turn(s).")
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"[{agent_name}] → {block.name}({list(block.input.keys())})")
                    result = handle_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return f"[{agent_name}] Reached max turns ({max_turns}) without completing."
