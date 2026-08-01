---
title: "AI Workspace overview"
description: "Centrally manage AI Gateway runtimes, LLM providers, App LLM proxies, MCP proxies, and AI policies from the AI Workspace control plane."
canonical_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/overview/
md_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/overview.md
tags:
  - cloud
  - ai-workspace
  - overview
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-01
content_type: "overview"
---

# AI Workspace overview

The AI Workspace is the control plane for AI Gateway runtimes. It gives platform teams one interface to register gateways, configure providers and application-facing proxies, apply policies, and manage deployments. You don't work directly with the Gateway-Controller API.

This page maps out the documentation in the order you work through it. To go straight to a running stack, follow [Get started with AI Workspace](getting-started.md).

## How it works

1. Create an AI Gateway entry in the AI Workspace, then start the gateway runtime and register it with the generated token.
2. Configure LLM providers, App LLM proxies, or MCP proxies in the control plane.
3. Deploy those configurations to one or more connected gateways.
4. Attach policies and guardrails, then redeploy to apply them.

## Set up the workspace

These topics cover standing the stack up and configuring how it runs:

| Topic | What it covers |
|-------|----------------|
| [Configuration and interpolation](configuration.md) | How each service loads `config.toml`, and how interpolation tokens inject environment values and mounted files |
| [Change the ports AI Workspace uses](ports.md) | Move the stack off its default ports |
| [Connect a database to the Platform API](database.md) | Move artifact storage from the default SQLite file onto PostgreSQL or SQL Server |
| [Authentication](authentication/overview.md) | File-based login for local use, or an OpenID Connect (OIDC) identity provider for production |

The {% raw %}`{{ env }}` and `{{ file }}`{% endraw %} tokens in `config.toml` supply the services' own startup credentials. They're a separate mechanism from [Secrets management](secrets-management.md), which stores the credentials your artifacts reference. Neither works in the other's place.

## Build the artifacts

| Topic | What it covers |
|-------|----------------|
| [AI Gateways](ai-gateways/setting-up.md) | The runtime that processes and routes requests between your applications and LLM providers. Register one, issue its registration token, and track its status |
| [LLM provider templates](llm-provider-templates/overview.md) | Reusable blueprints holding the endpoint, authentication, OpenAPI specification, and token mappings for an upstream service |
| [LLM providers](llm-providers/overview.md) | Connections to services such as OpenAI, Anthropic, Azure OpenAI, Gemini, Mistral AI, and AWS Bedrock |
| [App LLM proxies](llm-proxies/overview.md) | Optional application-facing endpoints, for when a GenAI application or agent needs its own controls |
| [MCP proxies](mcp-proxies/overview.md) | Managed endpoints in front of upstream Model Context Protocol (MCP) servers |
| [Secrets management](secrets-management.md) | Encrypted credentials that the artifacts above reference by handle instead of by value |

An LLM provider serves traffic on its own. Add an App LLM proxy only when one application or agent needs guardrails, authentication, exposed resources, or routing that differ from the provider's.

### Connect a provider that isn't built in

Built-in templates cover OpenAI, Azure OpenAI, Azure AI Foundry, AWS Bedrock, Anthropic, Mistral, and Gemini. For any other service, an organization admin creates a custom template under **Settings > LLM Provider Templates**. The template captures that service's endpoint, authentication shape, and token mappings, then appears in the provider type picker alongside the built-in ones.

A provider created from a custom template works only after you [deploy the template](llm-provider-templates/configure-template.md#deploy-a-custom-template-to-the-gateway) to the gateway that serves the provider.

### Three ways to create artifacts

| Path | How it works |
|------|--------------|
| In the AI Workspace | Configure the artifact in the console, then deploy it to one or more gateways. You own it, and it stays editable |
| [On the gateway](bottom-up-ai-artifact-deployment-guide.md) | Create it through the gateway's management API or its on-disk configuration. It serves traffic immediately and syncs up as a read-only copy the gateway owns |
| [Through CI/CD](ci-cd/overview.md) | Keep artifacts as project files in source control, validate them, and apply them with the `ap` CLI in a Git-based release workflow |

## Govern what you built

[Policies](policies/overview.md) attach to LLM providers, App LLM proxies, and MCP proxies. The AI Workspace is where you attach them, and the AI Gateway enforces them at request time.

- **Guardrails** — content safety, personally identifiable information (PII) masking, schema and length validation, and prompt injection detection.
- **Rate limits** — caps on request count, token consumption, and monetary spend.
- **Traffic and prompt policies** — model routing, prompt templates, semantic caching, and provider transformation.

[Insights](insights.md) -  The gateway publishes traffic, token usage, latency, cost, and guardrail events to your Moesif analytics workspace. Use those measurements to set limits from observed usage rather than estimates.

### Custom policies

When the built-in catalog doesn't cover what you need, write your own AI policy and ship it inside a gateway image. Once a gateway runs it, the policy syncs into the AI Workspace and appears under **Settings > Custom Policies**, ready to attach like any built-in policy.

1. [Writing an AI policy](policies/writing-an-ai-policy.md): implement the policy with the gateway SDK.
2. [Building the gateway with AI policies](policies/build-gateway-with-ai-policies.md): package it into a custom AI Gateway image with the `ap` CLI.
3. [Apply AI policies to proxies](policies/apply-ai-policies-to-proxies.md): sync it to the organization and attach it to a provider or proxy.

## Consume it from an application

| Topic | What it covers |
|-------|----------------|
| [GenAI applications](genai-applications.md) | Group API keys under a named application, for usage visibility per application |
| [Configure inbound authentication](configure-inbound-auth.md) | Set the header name clients use to send their API key |
| [Invoke providers and proxies via SDKs](using-sdks.md) | Call a deployed endpoint from the OpenAI, Anthropic, Gemini, Mistral, Azure OpenAI, or LangChain SDKs |

## Relationship to AI Gateway

The AI Workspace is the control plane. The [AI Gateway](../../cloud/ai-gateway/overview.md) is the runtime plane that handles the traffic.

- Use the AI Gateway docs to work directly with the runtime, the Gateway-Controller API, or the standalone deployment model.
- Use the AI Workspace docs for centralized lifecycle management of connected gateways and their AI assets.

## Next step

[Get started with AI Workspace](getting-started.md): run the stack locally with Docker Compose, create your first AI gateway, and configure an LLM provider.
