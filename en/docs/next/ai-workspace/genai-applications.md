---
title: "GenAI applications"
description: "Group API keys under a named GenAI application for application-level usage visibility, analytics, and governance."
canonical_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/genai-applications/
md_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/genai-applications.md
tags:
  - cloud
  - ai-workspace
  - genai-applications
author: WSO2 API Platform Documentation Team
last_updated: 2026-06-22
content_type: "concept"
---

# GenAI Applications

A GenAI application represents a real AI application inside AI Workspace, with the API keys it uses attached to it. This gives you application-level visibility and control instead of tracking usage only at the individual key level.

Without GenAI applications, usage is tied only to the API keys generated for LLM providers or App LLM proxies. That makes it hard to tell which application consumes which models, tokens, and cost, especially when several developers generate keys for the same project.

With a GenAI application, you can:

- Group API keys under a named application
- View usage and analytics at the application level
- Improve governance and accountability for shared GenAI workloads

## When to Use GenAI Applications

Use a GenAI application when:

- Multiple developers work on the same AI application
- The application uses more than one API key
- You want analytics grouped by application rather than by key alone
- Platform teams need clearer visibility into which applications drive usage

Examples include customer support copilots, internal knowledge assistants, document analysis apps, or workflow-specific AI agents.

## How It Works

The typical flow is:

1. Generate one or more API keys for an LLM provider or App LLM proxy.
2. Create a GenAI application in the AI Workspace.
3. Attach the generated API keys to that application.
4. Invoke the gateway using those mapped keys.
5. View analytics and usage for that application in Insights.

The same application can have multiple API keys mapped to it. This is useful when different developers, environments, or services within the same project need separate keys while still rolling up usage to one application.

## Prerequisites

- At least one configured [LLM provider](llm-providers/configure-provider.md) or [App LLM proxy](llm-proxies/configure-proxy.md)
- At least one generated API key
- Access to the AI Workspace project that holds the GenAI application

## Create a GenAI Application

1. Navigate to **AI Workspace** in your API Platform dashboard.
2. Open **GenAI Applications** from the left navigation menu.
3. Click **+ Create Application**.
4. Provide the application details:

    - **Name**: A human-readable name for the application
    - **Description**: Optional details to identify the app's purpose

5. Click **Create**.

The application is created within the current project and becomes the shared representation of that GenAI workload.

## Attach API Keys to an Application

After creating the application, attach the API keys that the application already uses.

1. Open the GenAI application.
2. Go to the **API Keys** section.
3. Click **Attach API Keys**.
4. Select one or more API keys generated for your LLM providers or App LLM proxies.
5. Save the mapping.

Only existing keys are mapped. This workflow does not create new keys. It links previously generated keys to the application so usage can be attributed correctly.

## View and Manage Attached Keys

The GenAI application details page shows the keys mapped to the application.

For each mapped key, you can view details such as:

- The associated provider or proxy
- The key status
- The user who created the key
- The creation and update timestamps
- The expiry details, when applicable

You can remove mappings for keys that should no longer be associated with the application.

Removing a mapping only detaches the key from that GenAI application. It does not delete the underlying key unless you remove it from the provider or proxy separately.

## Insights for GenAI Applications

Once a mapped key is used to invoke the gateway, the gateway can identify the owning GenAI application and publish analytics accordingly.

This lets you analyze usage by application, including:

- Request volume
- Token consumption
- Latency trends
- Error patterns
- Cost and resource usage by application

This is especially useful for teams that need to understand which GenAI applications are driving traffic and spend.

See [Insights](insights.md) for more on the analytics experience.

## Best Practices

- Create one GenAI application per real application or agent workload, not per developer.
- Map all keys used by the same application so analytics stay complete.
- Use clear names such as `Docs Assistant`, `Support Copilot`, or `Invoice Analyzer`.
- Review mappings periodically and remove keys that are no longer in use.
- Combine GenAI applications with App LLM proxies when an application also needs its own authentication, guardrails, or routing behavior.

## Related

- [App LLM proxies overview](llm-proxies/overview.md): create application-specific endpoints and controls
- [Insights](insights.md): analyze usage by application
- [Invoke providers and proxies via SDKs](using-sdks.md): use mapped keys when calling providers and proxies