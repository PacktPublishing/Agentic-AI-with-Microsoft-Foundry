"""
End-to-end demo runner for the IT helpdesk agent.

Demonstrates the MCP approval polling pattern: MCP tool calls require
explicit approval by default, providing human-in-the-loop oversight.
This script auto-approves read operations and requires console
confirmation for write operations (issue / work-item creation).
"""
import time

from azure.ai.agents.models import (
    ListSortOrder,
    MessageTextContent,
    RequiredMcpToolCall,
    ToolApproval,
)

from helpdesk_agent import helpdesk_agent, project


SAMPLE_TICKET = """
Reporter: support engineer
Severity: appears to be P2 (degraded)
Description:
Multiple users in the cardiology department are reporting that the
internal patient-lookup dashboard is returning 503 errors when filtering
by encounter date. The same dashboard works fine when filtering by MRN.
Please check whether there is an open issue for this in the internal
work-item tracker, search the knowledge base for the 503 troubleshooting
runbook, and if nothing exists, create a properly categorized work item.
"""


# Read-only MCP tools we are willing to auto-approve. Anything else
# (create_issue, create_work_item) requires explicit human approval.
AUTO_APPROVE_TOOLS = {
    "list_issues",
    "get_issue",
    "search_code",
    "list_work_items",
    "get_work_item",
    "search_wiki",
}


# Create thread and run
thread = project.agents.threads.create()
project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content=SAMPLE_TICKET,
)
run = project.agents.runs.create(
    thread_id=thread.id,
    agent_id=helpdesk_agent.id,
)


# Poll for status and handle MCP approvals as they arrive
while run.status in ("queued", "in_progress", "requires_action"):
    time.sleep(1)
    run = project.agents.runs.get(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        approvals = []

        for call in tool_calls:
            if isinstance(call, RequiredMcpToolCall):
                print(f"\nMCP approval requested:")
                print(f"  Server: {call.server_label}")
                print(f"  Tool:   {call.tool_name}")

                if call.tool_name in AUTO_APPROVE_TOOLS:
                    decision = True
                    print("  → auto-approved (read-only)")
                else:
                    answer = input("  Approve write operation? [y/N]: ")
                    decision = answer.strip().lower() == "y"
                    print(f"  → {'approved' if decision else 'rejected'}")

                approvals.append(
                    ToolApproval(
                        tool_call_id=call.id,
                        approve=decision,
                        headers=call.headers if hasattr(call, "headers") else {},
                    )
                )

        run = project.agents.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_approvals=approvals,
        )


# Print the agent response
if run.status == "completed":
    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING,
    )
    for msg in messages:
        if msg.role == "assistant":
            for content in msg.content:
                if isinstance(content, MessageTextContent):
                    print(content.text.value)
else:
    print(f"Run ended with status: {run.status}")


# Clean up resources after testing
project.agents.threads.delete(thread_id=thread.id)
project.agents.delete_agent(agent_id=helpdesk_agent.id)
print("\nResources cleaned up successfully")
