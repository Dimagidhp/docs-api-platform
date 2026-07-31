---
title: "Configure LLM instructions for the API Portal & MCP Hub"
description: "Set the portal name and description that head llms.txt, and turn AI discoverability on or off for the whole portal."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/admin-settings/llm-instructions/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/admin-settings/llm-instructions.md
tags:
  - cloud
  - api-portal
  - ai-discovery
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-31
content_type: "how-to"
---

# LLM Instructions

**LLM Instructions** controls how AI agents see your portal as a whole. It sets the name and description at the top of `llms.txt` — the first thing an agent reads before it navigates anything else — and carries the switch that turns AI discoverability on or off for the entire portal.

Everything on this page is scoped to one [view](manage-views.md). Use the view selector to switch.

## Open the Page

Go to **Settings** and select **LLM Instructions** under **AI & DISCOVERY**.

![LLM Instructions page with the Portal is AI-discoverable toggle, Portal name and Description fields, a Publish button, and a live preview of the generated llms.txt](../../../assets/img/devportal/llm-instructions.png)

## Turn AI Discoverability On or Off

The **Portal is AI-discoverable** card at the top shows the view's live `llms.txt` path and a toggle.

Switching it off makes every agent-facing endpoint return `404` — `llms.txt` itself, the API and MCP catalogs, per-artifact Markdown, raw specifications, and every workflow endpoint. It overrides each artifact's own agent-visibility setting, so nothing reaches an agent while it's off.

The **Publish** button stays clickable when the toggle is off, so you can save the change.

## Set the Portal Identity

Two fields make up the instructions, and both appear verbatim at the top of `llms.txt`.

| Field | What it does |
|---|---|
| **Portal name** | Replaces the default `{orgName} API Portal` heading |
| **Description** | The paragraph below the name. This is the orientation text agents read first |

The description is a free-text area, not a one-liner. Use it for the context an agent can't infer from individual API specs:

- What the portal covers and what kinds of APIs it exposes
- How the catalog is organized — by domain, team, or lifecycle stage
- Authentication conventions that apply across APIs
- Which workflows are the recommended starting points for common tasks
- Usage policies or limitations agents should respect

Leave either field empty and the portal falls back to its defaults: `{orgName} API Portal` for the heading, and a generic one-line description.

Click **Publish** to save. Changes take effect immediately — the next request for `llms.txt` reflects them.

## Preview the Result

The pane beside the fields renders the `llms.txt` your settings produce, and refreshes as you type, so you can see the header in context above the generated API and workflow index. The icon in its corner opens the live `llms.txt` in a new tab.

To fetch it yourself:

```text
GET /{orgName}/views/{viewName}/llms.txt
```

![llms.txt file showing API Workflows section with workflow names, descriptions, and spec links](../../../assets/img/devportal/llms-txt.png)

Only your name and description are editable. Everything below them — the API Workflows, APIs, MCPs, GraphQL, WebSocket, and WebSub sections — is generated from the catalog and reflects each artifact's own agent visibility. See [AI Agent Discovery](../discover-apis/ai-agent-discovery.md) for how that index is built.

## Related

- [AI Agent Discovery](../discover-apis/ai-agent-discovery.md): every agent-facing endpoint, and what `llms.txt` contains
- [Managing API Workflows](managing-api-workflows.md): per-workflow agent visibility
- [Make an API AI-Ready](../../../cloud/develop-api-proxy/make-api-ai-ready.md): per-API agent visibility, and writing descriptions agents can use
- [Manage Views](manage-views.md): why these settings are per-view
