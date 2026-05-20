"""
Case Study 2: Enterprise IT Helpdesk Agent with MCP Integration
Chapter 8 — Advanced Agent Capabilities and Tool Integration

Uses two MCP servers (GitHub + Azure DevOps) and one Azure AI Search
index, demonstrating how MCP's auto-discovery and standardized protocol
collapse what would otherwise be three separate integration projects
into a single cohesive agent.
"""
import os

from azure.ai.agents.models import (
    AzureAISearchTool,
    AzureAISearchQueryType,
    McpTool,
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
# MCP Tool 1: GitHub integration
# -----------------------------------------------------------------------------
github_mcp = McpTool(
    server_label="github",
    server_url="https://mcp.github.com/sse",
    headers={"Authorization": "Bearer <github-token>"},
    allowed_tools=[
        {"name": "list_issues"},
        {"name": "get_issue"},
        {"name": "create_issue"},
        {"name": "search_code"},
    ],
)


# -----------------------------------------------------------------------------
# MCP Tool 2: Azure DevOps integration
# -----------------------------------------------------------------------------
devops_mcp = McpTool(
    server_label="azure-devops",
    server_url="https://mcp.dev.azure.com/sse",
    headers={"Authorization": "Bearer <devops-token>"},
    allowed_tools=[
        {"name": "list_work_items"},
        {"name": "get_work_item"},
        {"name": "create_work_item"},
        {"name": "search_wiki"},
    ],
)


# -----------------------------------------------------------------------------
# Knowledge base for troubleshooting guides (Azure AI Search, not MCP,
# because the internal index is not exposed as an MCP server)
# -----------------------------------------------------------------------------
kb_search = AzureAISearchTool(
    index_connection_id="<search-connection-id>",
    index_name="it-knowledge-base",
    query_type=AzureAISearchQueryType.SEMANTIC,
    top_k=5,
)


# -----------------------------------------------------------------------------
# Create unified IT helpdesk agent
# -----------------------------------------------------------------------------
helpdesk_agent = project.agents.create_agent(
    model="gpt-4o",
    name="it-helpdesk",
    instructions="""You are an IT helpdesk agent.

    WORKFLOW:
    1. Classify the issue and route appropriately:
       - Open-source project → search GitHub first
       - Internal system → search Azure DevOps first
       - General IT → search knowledge base first
    2. Search for existing related issues before creating new ones
    3. Provide troubleshooting steps from the knowledge base
    4. If unresolved, create a properly categorized ticket

    RULES:
    - Never expose internal system details in GitHub issues
    - Classify severity: P1 (system down), P2 (degraded), P3 (minor)
    - For P1 issues, immediately create a work item AND notify
    - Always search before creating to avoid duplicate tickets""",
    tools=[github_mcp, devops_mcp, kb_search],
)
print(f"IT helpdesk agent created: {helpdesk_agent.id}")
