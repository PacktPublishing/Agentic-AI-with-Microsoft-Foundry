# Case Study 2: Enterprise IT Helpdesk Agent with MCP Integration

Companion code for **Chapter 8 — Advanced Agent Capabilities and Tool Integration**, *Agentic AI with Microsoft Foundry* (Packt, 2026).

This case study builds a unified IT helpdesk agent that searches across GitHub (open-source projects), Azure DevOps (internal systems), and an internal Azure AI Search knowledge base — all through a single conversational interface. The architecture demonstrates how MCP's auto-discovery and standardized protocol collapse what would otherwise be three separate integration projects into a single cohesive agent.

## Files

| File | Purpose |
|---|---|
| `helpdesk_agent.py` | Defines `github_mcp`, `devops_mcp`, `kb_search`, and the `helpdesk_agent` itself |
| `run_demo.py` | Sends a sample ticket, handles MCP approvals, prints the response, cleans up |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

## Why MCP over OpenAPI here

MCP was chosen over OpenAPI for this architecture because both GitHub and Azure DevOps ship officially maintained MCP servers. Building equivalent integrations with OpenAPI would have required authoring and maintaining two separate specifications (roughly 40 endpoints each), implementing their authentication flows, and updating the specs every time GitHub or Microsoft shipped API changes. With MCP, the agent auto-discovers the available operations at connection time, and API evolution becomes the upstream maintainers' responsibility rather than ours.

OpenAPI would still have been the right choice for a purely internal API we owned end-to-end — but for integration with two rapidly evolving third-party platforms, MCP's auto-discovery and standardized protocol materially reduced the integration surface.

## Prerequisites

- An active Azure subscription with an Azure AI Foundry project (see Chapter 2 for setup)
- Python 3.10 or later
- A deployed GPT-4o model (or any newer model from the Foundry catalog)
- A GitHub personal access token (classic) with repository read and issue write permissions
- An Azure DevOps personal access token with work-item read/write permissions
- An Azure AI Search index named `it-knowledge-base` registered as a Foundry connection

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Authenticate with Azure
az login

# 3. Copy and edit the environment file
cp .env.example .env
# then edit .env with your Foundry endpoint

# 4. Edit helpdesk_agent.py and replace these placeholders with your values:
#      <github-token>           in the GitHub McpTool headers
#      <devops-token>           in the Azure DevOps McpTool headers
#      <search-connection-id>   in the kb_search AzureAISearchTool
```

## Run

```bash
python run_demo.py
```

The demo script implements the **MCP approval polling pattern** described in the chapter:

- Read-only operations (`list_issues`, `get_issue`, `search_code`, `list_work_items`, `get_work_item`, `search_wiki`) are auto-approved
- Write operations (`create_issue`, `create_work_item`) prompt the operator for explicit approval in the console

This mirrors the production governance pattern — start with read-only integrations to build confidence, then gradually enable write operations with appropriate approval workflows.

## Security note: `allowed_tools` is a capability manifest

The `allowed_tools` parameter on each `McpTool` is critical for security — it restricts which MCP server tools the agent can access. If `allowed_tools` is omitted or left unrestricted, the agent inherits every capability the MCP server exposes — which, for a server like GitHub, can include repository deletion, force-pushing to protected branches, or rotating organization secrets. A prompt-injection attack or an over-eager model response could therefore trigger destructive operations that were never intended to be part of the agent's scope.

Treat the `allowed_tools` list as a capability manifest reviewed the same way you would review IAM policies, and only widen it after the new tools have been evaluated in a non-production environment.

## Evaluation results (from the chapter)

Evaluated over a four-week pilot (early 2026) with the IT support team, with metrics collected through Azure Monitor dashboards and compared against the four-week baseline period immediately prior to deployment:

- Average ticket resolution time reduced significantly
- Duplicate ticket creation decreased due to automated search-before-create
- First-contact resolution rate improved with knowledge base integration
- Support engineer context-switching eliminated unnecessary routine queries

These results are illustrative, based on typical patterns observed in similar deployments.

## Key takeaway

MCP integration dramatically reduces the engineering effort required to connect agents to multiple enterprise platforms. The standardized protocol means you can add new system integrations by simply connecting to additional MCP servers, without modifying the agent's core logic.

For teams evaluating MCP adoption, start with read-only integrations (searching and retrieving data) to build confidence, then gradually enable write operations with appropriate approval workflows.
