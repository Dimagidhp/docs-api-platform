---
title: "AI Workspace overview"
description: "Centrally manage AI Gateway runtimes, LLM providers, App LLM proxies, MCP proxies, and AI policies from the AI Workspace control plane."
canonical_url: https://wso2.com/api-platform/docs/next/ai-workspace/overview/
md_url: https://wso2.com/api-platform/docs/next/ai-workspace/overview.md
tags:
  - cloud
  - ai-workspace
  - overview
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-01
content_type: "overview"
---

# AI Workspace overview

AI Workspace is where a platform team configures and governs the traffic its organization sends to large language model (LLM) services.

The starting point is an AI Gateway: a runtime that sits between your applications and services such as OpenAI, Anthropic, or AWS Bedrock. Your applications call the gateway instead of calling those services directly, and the gateway forwards each request upstream. AI Workspace is the console where you decide what the gateway does. From there you set which services it can reach, which credentials it uses, what limits and safety checks it applies, and which applications get through.

Putting the gateway in the middle moves five things out of your application code and into one place:

- **Credentials.** Upstream API keys are stored encrypted and referenced by handle, so no application holds one.
- **Limits.** Cap requests, token consumption, and monetary spend per provider, per endpoint, or per application.
- **Safety.** Attach guardrails for content moderation, personally identifiable information (PII) masking, and prompt injection detection.
- **Visibility.** See traffic, tokens, latency, and cost broken down by application and consumer.
- **Endpoints.** Applications call a stable URL, so you can change the provider behind it without changing clients.

This page introduces the pieces and maps out the documentation in the order you work through it. To go straight to a running stack, follow [Get started with AI Workspace](getting-started.md).

## The pieces

You'll meet these objects throughout the documentation:

| Object | What it is |
|--------|------------|
| **AI Gateway** | The runtime that processes and routes requests between your applications and LLM providers. You register it in the workspace and run it wherever you need it |
| **LLM provider** | A connection to an upstream AI service, holding its endpoint and credentials. Serves traffic on its own once deployed |
| **App LLM proxy** | An optional application-facing endpoint layered on a provider, for when one GenAI application or agent needs controls of its own |
| **MCP proxy** | A managed endpoint in front of an upstream Model Context Protocol (MCP) server |
| **Policy** | A rule the gateway enforces on each request—a guardrail, a rate limit, or a routing or prompt behavior |
| **Secret** | An encrypted credential that the objects above reference by handle instead of by value |

## How it works

1. Create an AI Gateway entry in AI Workspace, then start the gateway runtime and register it with the generated token.
2. Configure LLM providers, App LLM proxies, or MCP proxies in the control plane.
3. Deploy those configurations to one or more connected gateways.
4. Attach policies and guardrails, then redeploy to apply them.

Nothing you configure affects live traffic until you deploy it. That applies to later edits too: change a setting, then redeploy it to the gateways that serve it.

## Set up the workspace

These topics cover standing the stack up and configuring how it runs:

| Topic | What it covers |
|-------|----------------|
| [Configuration and interpolation](setting-up/configuration.md) | How each service loads `config.toml`, and how interpolation tokens inject environment values and mounted files |
| [Change the ports AI Workspace uses](setting-up/ports.md) | Move the stack off its default ports |
| [Connect a database to the Platform API](setting-up/database.md) | Move artifact storage from the default SQLite file onto PostgreSQL or SQL Server |
| [Authentication](setting-up/authentication/overview.md) | File-based login for local use, or an OpenID Connect (OIDC) identity provider for production |

The {% raw %}`{{ env }}` and `{{ file }}`{% endraw %} tokens in `config.toml` supply the services' own startup credentials. They're a separate mechanism from [Secrets management](secrets-management.md), which stores the credentials your artifacts reference. Neither works in the other's place.

## Build the artifacts

| Topic | What it covers |
|-------|----------------|
| [Set up an AI Gateway](ai-gateways/setting-up.md) | Register a gateway, issue its registration token, connect the runtime, and track its status |
| [LLM provider templates](llm-provider-templates/overview.md) | Reusable blueprints holding the endpoint, authentication, OpenAPI specification, and token mappings for an upstream service |
| [LLM providers](llm-providers/overview.md) | Connections to services such as OpenAI, Anthropic, Azure OpenAI, Gemini, Mistral AI, and AWS Bedrock |
| [App LLM proxies](llm-proxies/overview.md) | Add an application-facing endpoint when one GenAI application or agent needs controls of its own |
| [MCP proxies](mcp-proxies/overview.md) | Put a managed endpoint in front of an upstream MCP server |
| [Secrets management](secrets-management.md) | Encrypted credentials that the artifacts above reference by handle instead of by value |

An LLM provider serves traffic on its own. Add an App LLM proxy only when one application or agent needs guardrails, authentication, exposed resources, or routing that differ from the provider's.

### Connect a provider that isn't built in

Built-in templates cover OpenAI, Azure OpenAI, Azure AI Foundry, AWS Bedrock, Anthropic, Mistral, and Gemini. For any other service, an organization admin creates a custom template under **Settings > LLM Provider Templates**. The template captures that service's endpoint, authentication shape, and token mappings, then appears in the provider type picker alongside the built-in ones.

A provider created from a custom template works only after you [deploy the template](llm-provider-templates/configure-template.md#deploy-a-custom-template-to-the-gateway) to the gateway that serves the provider.

### Three ways to create artifacts

| Path | How it works |
|------|--------------|
| In AI Workspace | Configure the artifact in the console, then deploy it to one or more gateways. You own it, and it stays editable |
| [On the gateway](sync-gateway-created-artifacts.md) | Create it through the gateway's management API or its on-disk configuration. It serves traffic immediately and syncs up as a read-only copy the gateway owns |
| [Through CI/CD](ci-cd/overview.md) | Keep artifacts as project files in source control, validate them, and apply them with the `ap` CLI in a Git-based release workflow |

## Govern what you built

[Policies](policies/overview.md) attach to LLM providers, App LLM proxies, and MCP proxies. AI Workspace is where you attach them; the AI Gateway enforces them at request time.

- **Guardrails**—content safety, PII masking, schema and length validation, and prompt injection detection.
- **Rate limits**—caps on request count, token consumption, and monetary spend.
- **Traffic and prompt policies**—model routing, prompt templates, semantic caching, and provider transformation.

The gateway also publishes traffic, token usage, latency, cost, and guardrail events to your Moesif analytics workspace. [Insights](insights.md) is where you open it. Set your limits from those measurements rather than from estimates.

### Custom policies

When the built-in catalog doesn't cover what you need, write your own AI policy and ship it inside a gateway image. Once a gateway runs it, the policy syncs into AI Workspace and appears under **Settings > Custom Policies**, ready to attach like any built-in policy.

1. [Write an AI policy](policies/writing-an-ai-policy.md): implement the policy with the gateway SDK.
2. [Build the gateway with AI policies](policies/build-gateway-with-ai-policies.md): package it into a custom AI Gateway image with the `ap` CLI.
3. [Apply AI policies to proxies](policies/apply-ai-policies-to-proxies.md): sync it to the organization and attach it to a provider or proxy.

## Consume it from an application

| Topic | What it covers |
|-------|----------------|
| [GenAI applications](genai-applications.md) | Group API keys under a named application, for usage visibility per application |
| [Configure inbound authentication](configure-inbound-auth.md) | Set the header name clients use to send their API key |
| [Invoke providers and proxies via SDKs](using-sdks.md) | Call a deployed endpoint from the OpenAI, Anthropic, Gemini, Mistral, Azure OpenAI, or LangChain SDKs |

## Control plane and data plane

AI Workspace and the [AI Gateway](../../cloud/ai-gateway/overview.md) are two halves of one system, and the split tells you where a given task belongs.

| | AI Workspace | AI Gateway |
|---|---|---|
| **Role** | Control plane | Data plane |
| **What it holds** | Your artifacts, policies, and credentials, plus a record of where each one is deployed | The configuration deployed to it, and the traffic passing through |
| **What you do there** | Add, edit, and delete artifacts, attach policies, deploy and undeploy them, and check what's running where | Run the runtime and register it against the control plane |
| **When it acts** | When you save and deploy | On every request |

One gateway can serve many artifacts, and one artifact can be deployed to many gateways. The workspace keeps track of that mapping in both directions, so you don't have to inspect a gateway to learn what's on it:

- An artifact's **Deployed Gateways** section lists every gateway it's deployed to, with the deployment status of each.
- The **Deploy to Gateway** page shows a deployment ID and status per gateway, alongside a deployment history timeline, and it's where you stop a deployment to undeploy the artifact.
- The **AI Gateways** list shows whether each gateway runtime is **Active** or **Not Active**.

Working through the workspace means you manage all of this from the console rather than calling the gateway's Gateway-Controller API yourself.

Use the AI Workspace documentation for centralized lifecycle management of your connected gateways and the AI artifacts on them. Use the [AI Gateway documentation](../../cloud/ai-gateway/overview.md) when you work with the runtime directly. That covers its Gateway-Controller API, its on-disk configuration, and the standalone deployment model where there's no control plane at all.

An artifact created on a gateway isn't invisible to the workspace. It [syncs up as a read-only copy](sync-gateway-created-artifacts.md) you can view and monitor.

## Next step

[Get started with AI Workspace](getting-started.md): run the stack locally with Docker Compose, create your first AI gateway, and configure an LLM provider.
