"""
Case Study 1: Healthcare Prior Authorization Agent
Chapter 8 — Advanced Agent Capabilities and Tool Integration

Combines three tools introduced earlier in the chapter:
  - policy_search   (AzureAISearchTool) — medical necessity criteria
  - CodeInterpreterTool                  — historical approval pattern analysis
  - prior_auth_tool (LogicAppTool)       — authorization submission

In a fuller production deployment you would also wire in an OpenAPI or
Azure Function tool for EHR clinical-history retrieval, following the
same pattern as the scheduling OpenAPI tool earlier in the chapter.
"""
import os

from azure.ai.agents.models import (
    AzureAISearchTool,
    AzureAISearchQueryType,
    CodeInterpreterTool,
    LogicAppTool,
)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


# -----------------------------------------------------------------------------
# Initialize the project client
# -----------------------------------------------------------------------------
credential = DefaultAzureCredential()
project = AIProjectClient(
    endpoint=os.environ.get(
        "AZURE_AI_FOUNDRY_ENDPOINT",
        "https://<your-project>.services.ai.azure.com",
    ),
    credential=credential,
)


# -----------------------------------------------------------------------------
# Tool 1: Azure AI Search for medical necessity criteria
# (Reproduced here from the "Azure AI Search Tool" section earlier in the
# chapter. In a multi-file project you would import this from a shared
# tools module.)
# -----------------------------------------------------------------------------
policy_search = AzureAISearchTool(
    index_connection_id="<your-search-connection-id>",
    index_name="payer-medical-necessity-policies",
    query_type=AzureAISearchQueryType.SEMANTIC,
    top_k=5,
)


# -----------------------------------------------------------------------------
# Tool 3: Logic Apps for authorization submission
# (Reproduced from the "Automating Enterprise Workflows with Logic Apps"
# section earlier in the chapter.)
# -----------------------------------------------------------------------------
prior_auth_tool = LogicAppTool(
    name="submit_prior_auth",
    description="Submit a prior authorization request for a medical procedure",
    logic_app_connection_id="<your-logic-app-connection-id>",
    workflow_name="PriorAuthorizationWorkflow",
)


# -----------------------------------------------------------------------------
# Create the prior authorization agent
# -----------------------------------------------------------------------------
prior_auth_agent = project.agents.create_agent(
    model="gpt-4o",
    name="prior-auth-specialist",
    instructions="""You are a prior authorization specialist agent.

    WORKFLOW:
    Step 1: Extract patient ID, insurance plan, procedure code
    (CPT/HCPCS), clinical indication, and diagnosis (ICD-10).

    Step 2: Search payer policies to determine if prior auth is
    required and what medical necessity criteria must be met.

    Step 3: Compare clinical indication against payer criteria.
    Identify missing documentation and flag potential issues.

    Step 4: If criteria are met, submit authorization via workflow
    tool. Provide reference number and expected timeline.

    Step 5: If criteria are NOT met, list specific deficiencies
    and suggest additional documentation needed.

    RULES:
    - Always verify patient eligibility before proceeding
    - Never auto-submit if medical necessity is unclear
    - Maintain a complete audit trail of all decisions
    - Cite specific policy sections in your determinations""",
    tools=[policy_search, CodeInterpreterTool(), prior_auth_tool],
)
print(f"Prior authorization agent created: {prior_auth_agent.id}")
