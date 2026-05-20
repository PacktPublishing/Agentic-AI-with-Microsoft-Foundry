"""
End-to-end demo runner for the prior authorization agent.

Sends a sample prior authorization request through the agent and prints
the response. Cleans up the agent and thread when finished — failing to
clean up leaves orphaned resources in your Foundry project that count
against quotas and (for vector stores) incur storage cost.
"""
from azure.ai.agents.models import ListSortOrder, MessageTextContent

from prior_auth_agent import prior_auth_agent, project


SAMPLE_REQUEST = """
Patient ID: 78451
Insurance Plan: BlueCross PPO
Procedure Code (CPT): 72148  (MRI lumbar spine without contrast)
Diagnosis (ICD-10): M54.5, M51.36
Clinical indication: 8-week history of lower back pain radiating down
the left leg with worsening symptoms despite 6 weeks of physical
therapy and NSAIDs. Decreased sensation in left L5 dermatome; left
great toe extension graded 4/5.

Please determine if prior authorization is required and, if so,
whether medical necessity criteria are met.
"""


# Create a thread and send the request
thread = project.agents.threads.create()
project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content=SAMPLE_REQUEST,
)

# Run the agent
run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=prior_auth_agent.id,
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

# Clean up resources
project.agents.threads.delete(thread_id=thread.id)
project.agents.delete_agent(agent_id=prior_auth_agent.id)
print("\nResources cleaned up successfully")
