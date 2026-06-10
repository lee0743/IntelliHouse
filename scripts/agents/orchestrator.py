"""Agent 4: Orchestrates the multi-agent loop (content → structure → critic → repeat)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import anthropic
from agents import content_agent, structure_agent, critic_agent
from config import MAX_ITERATIONS


def run(client: anthropic.Anthropic, task: str, verbose: bool = True) -> dict:
    """
    Orchestration loop:
      1. Run Content Agent (Agent 1)
      2. Run Structure Agent (Agent 2)
      3. Run Critic Agent (Agent 3)
      4. If REVISION_NEEDED and iterations remain → loop back to 1 with feedback
      5. On APPROVE or max iterations → return final report
    """

    def log(msg: str):
        if verbose:
            print(f"[Orchestrator] {msg}")

    content_feedback = ""
    structure_feedback = ""
    content_result = {}
    structure_result = {}
    critic_result = {}

    for iteration in range(1, MAX_ITERATIONS + 1):
        log(f"─── Iteration {iteration}/{MAX_ITERATIONS} ───")

        log("Running Agent 1 (Content)...")
        content_result = content_agent.run(client, task, critic_feedback=content_feedback)
        log(f"Content Agent: changed {len(content_result.get('files_changed', []))} file(s).")

        log("Running Agent 2 (Structure)...")
        structure_result = structure_agent.run(client, task, critic_feedback=structure_feedback)
        log(f"Structure Agent: changed {len(structure_result.get('files_changed', []))} file(s), "
            f"moved {len(structure_result.get('files_moved', []))} file(s).")

        log("Running Agent 3 (Critic)...")
        critic_result = critic_agent.run(client, task, content_result, structure_result, iteration)
        verdict = critic_result.get("verdict", "APPROVE")
        log(f"Critic verdict: {verdict} — {critic_result.get('overall', '')}")

        if verdict == "APPROVE":
            log("✓ Approved. Work complete.")
            break

        if iteration < MAX_ITERATIONS:
            content_feedback = critic_result["feedback"].get("content_agent", "")
            structure_feedback = critic_result["feedback"].get("structure_agent", "")
            log("Revision requested. Re-running agents with feedback...")
        else:
            log(f"⚠ Max iterations ({MAX_ITERATIONS}) reached. Finalizing with best result.")

    return {
        "iterations": iteration,
        "final_verdict": critic_result.get("verdict", "APPROVE"),
        "content_result": content_result,
        "structure_result": structure_result,
        "critic_overall": critic_result.get("overall", ""),
    }
