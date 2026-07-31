---
title: "App LLM proxies overview"
description: "Add an application-facing endpoint on top of an LLM provider for app- or agent-specific authentication, guardrails, and access controls."
canonical_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/llm-proxies/overview/
md_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/llm-proxies/overview.md
tags:
  - cloud
  - ai-workspace
  - llm-proxies
author: WSO2 API Platform Documentation Team
last_updated: 2026-06-22
content_type: "overview"
---

# App LLM Proxies Overview

## Why a Proxy on Top of a Provider?

An **LLM Provider** connects the gateway to an upstream LLM service and can be called directly. An **App LLM Proxy** adds an optional, application-facing endpoint on top when you need controls that are specific to a GenAI application or agent.

The main benefit is specialization and isolation. You can call a single provider directly, or back multiple App LLM proxies with it: one for a customer-facing chatbot with strict guardrails, another for an internal agent with relaxed settings, and another for a workflow-specific GenAI assistant. You configure each proxy independently, and swapping the underlying provider needs no changes in the applications or agents that call the proxy.

## What You Can Do with an App LLM Proxy

**Expose a controlled API endpoint**
The proxy gives you a stable URL your GenAI application or agent calls. You control which resources (API paths) are exposed, and can enable or disable them without touching the upstream provider.

**Add app-specific controls only when needed**
If provider-level controls are sufficient, you can call the provider directly. Use an App LLM proxy only when a specific application or agent needs its own authentication, guardrails, exposed resources, or traffic controls.

**Enforce authentication**
Require applications or agents to present an API key before the gateway forwards their requests to the LLM. The workspace generates keys per proxy, and each key expires after 90 days.

**Apply guardrails**
Attach content safety, PII masking, or semantic caching policies globally across all endpoints, or target them at specific resources only.

**Create specialized endpoints for apps and agents**
Create separate proxies for different GenAI applications, agents, teams, or environments (dev, staging, production) — each with independent rate limits, guardrails, access keys, and exposed resources — all sharing the same provider backend.

**Switch providers without client changes**
Because applications and agents call the proxy URL rather than the provider directly, you can swap the underlying LLM provider (for example, from OpenAI to Azure OpenAI) without any changes on the client side.

## Next Steps

- [Configure an App LLM proxy](configure-proxy.md): create and deploy your first specialized proxy
- [Manage an App LLM proxy](manage-proxy.md): update configuration, guardrails, and resources after deployment
