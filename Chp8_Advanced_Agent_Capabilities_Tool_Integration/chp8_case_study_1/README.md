# Case Study 1: Healthcare Prior Authorization Agent

Companion code for **Chapter 8 — Advanced Agent Capabilities and Tool Integration**, *Agentic AI with Microsoft Foundry* (Packt, 2026).

This case study builds a prior authorization agent that automates a workflow traditionally taking 45 minutes per request down to under 10 minutes. The agent combines three tools introduced earlier in the chapter:

- **Azure AI Search** (`policy_search`) — medical necessity criteria and payer policies
- **Code Interpreter** — historical approval pattern analysis
- **Logic Apps** (`prior_auth_tool`) — authorization submission workflow

A fuller production deployment would also wire in an OpenAPI or Azure Function tool for EHR clinical-history retrieval, following the same pattern as the scheduling OpenAPI tool earlier in the chapter.

## Files

| File | Purpose |
|---|---|
| `prior_auth_agent.py` | Defines `policy_search`, `prior_auth_tool`, and the `prior_auth_agent` itself |
| `run_demo.py` | Sends a sample PA request, prints the response, cleans up |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

## Prerequisites

- An active Azure subscription with an Azure AI Foundry project (see Chapter 2 for setup)
- Python 3.10 or later
- A deployed GPT-4o model (or any newer model from the Foundry catalog — see Chapter 8 "Technical Requirements" for substitutes)
- An Azure AI Search index named `payer-medical-necessity-policies` (or update the index name in `prior_auth_agent.py`)
- A Logic App named `PriorAuthorizationWorkflow` with an HTTP trigger
- Both resources registered as connections in your Foundry project under **Settings → Connected resources**

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Authenticate with Azure
az login

# 3. Copy and edit the environment file
cp .env.example .env
# then edit .env with your Foundry endpoint

# 4. Edit prior_auth_agent.py and replace these placeholders with the
#    connection IDs from your Foundry project:
#      <your-search-connection-id>
#      <your-logic-app-connection-id>
```

## Run

```bash
python run_demo.py
```

You should see the agent:

1. Extract the patient ID, plan, CPT code, and diagnosis from the request
2. Search payer policies for the relevant medical necessity criteria
3. Compare the clinical indication against those criteria
4. If criteria are met, submit the authorization via the Logic App
5. Return a reference number and expected timeline (or list missing documentation if criteria are not met)

The script then deletes the agent and thread so they do not accumulate as orphaned resources.

## Evaluation results (from the chapter)

Evaluated against 200 historical PA cases with known outcomes:

- Authorization requirement detection: **97% accuracy**
- Medical necessity assessment: **94% agreement with specialist review**
- Average processing time: **7 minutes** (down from 45 minutes)
- Documentation completeness check: **96% of missing documents correctly identified**

These results are illustrative and represent typical performance ranges observed in similar production deployments.

## Key takeaway

Healthcare prior authorization automation requires multiple tools working in concert. The agent's value comes not from any single tool but from its ability to orchestrate policy lookup, eligibility verification, medical necessity determination, and workflow submission into a coherent, auditable process.

Organizations starting with prior authorization automation should begin with the policy search and medical necessity determination steps, then gradually add EHR integration and workflow submission as confidence in the system grows.
