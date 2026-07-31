---
title: "API Portal concepts"
description: "The key building blocks of the API Portal & MCP Hub — organization, views, labels, APIs, MCP servers, API workflows, subscription plans, applications, subscriptions, API keys, and more — and how they relate to each other."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/concepts/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/concepts.md
tags:
  - cloud
  - api-portal
  - concepts
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-31
content_type: "concept"
---

# Concepts

This page explains the key building blocks of the API Portal & MCP Hub and how they relate to each other.

## Organization

Each portal instance serves exactly **one organization** — the top-level container for the portal's APIs, MCP servers, applications, subscriptions, and users. The organization is pinned by `handle` in the `[api_portal.organization]` table of `config.toml`, and is seeded automatically on first startup. The portal refuses to start without a handle.

The database schema itself is multi-organization — one shared database can hold several organizations, each served by its own portal instance — but any single instance is bound to its configured organization, and a request scoped to a different organization is rejected.

The handle appears in every portal URL:

```
https://<host>/<orgHandle>/views/<viewName>
```

It must match the organization ID the Platform API asserts in the `org_handle` claim of the tokens this portal verifies. See [Organization Settings](admin-settings/organization-settings.md).

## View

A **view** is a filtered, branded subset of the organization's APIs and MCP servers — for example, one view for internal developers and one for external partners. Each view shows only the artifacts carrying its assigned labels, and can have its own layout, LLM instructions, and API workflows.

Each view has its own URL:

```
https://<host>/<orgHandle>/views/<viewName>
```

See [Manage Views](admin-settings/manage-views.md).

## Label

A **label** is a tag you assign to an API or MCP server to control which views expose it. A view shows only the artifacts carrying at least one of its assigned labels — so an artifact labelled `internal` appears only in views that include the `internal` label. Labels differ from an artifact's **tags**, which are informational and don't affect visibility. See [Manage Labels](admin-settings/manage-labels.md).

## Layout

A **layout** is a custom Handlebars template that defines the structure and styling of a view's pages (home, listing, detail). Layouts let you give each view its own branding, navigation, and page structure beyond what the theme color settings allow. See [Theming](admin-settings/theming.md) and [Design Mode](setting-up/design-mode.md) for building one offline.

## Artifact types

The portal serves three kinds of artifact: **APIs**, **MCP servers**, and **API workflows**. Which of them a given portal exposes is an operator setting — the `enabled_types` allowlist in the `[api_portal.artifacts]` config. A type that isn't enabled gets no navigation entry and no landing-page section, and its routes return `404`. See [Artifact types](artifact-types.md).

## API

An **API** is an entry in the portal catalog that developers can discover and subscribe to. The portal supports these API types:

| Type | Definition format |
|---|---|
| REST | OpenAPI (Swagger) YAML/JSON |
| GraphQL | GraphQL schema (SDL) |
| SOAP | WSDL/XML |
| WebSocket | AsyncAPI YAML/JSON |
| WebSub | AsyncAPI YAML/JSON |

Each API can have its own landing page content, documentation sections, icon, and banner image. APIs carry labels (which control view visibility) and tags (informational), and can be marked agent-visible so AI agents discover them. See [Manage APIs](admin-settings/manage-apis.md).

## MCP Server

An **MCP server** is a Model Context Protocol server published in the portal alongside your APIs — the "MCP Hub" half of the portal. Its contract is its **definition** — the tools, resources, and prompts it exposes — rather than an OpenAPI-style specification. MCP servers are managed, subscribed to, and secured with keys the same way APIs are, and can be marked agent-visible for AI agent discovery. See [Manage MCP Servers](admin-settings/manage-mcp-servers.md).

## API Workflow

An **API workflow** is a published, multi-step sequence of API calls defined in [Arazzo format](https://spec.openapis.org/arazzo/latest.html). Workflows are authored by admins and published per view for both human developers and AI agents to discover and follow. See [Managing API Workflows](admin-settings/managing-api-workflows.md) and [Consuming API Workflows](api-workflows/consuming-api-workflows.md).

## Subscription Plan

A **subscription plan** is a named usage tier that controls how much of an API or MCP server a developer can consume. Plans are attached to an artifact during publishing, and developers choose a plan when subscribing.

Plans can define rate limits — a request count (or event count, for async APIs) per time window (minute, hour, day, or month). When enabled, a default set of plans (Bronze, Silver, Gold, Unlimited, AsyncUnlimited) is created with the organization. See [Subscription Plans](admin-settings/subscription-plans.md).

## Application

An **application** is a logical container — representing a mobile app, web app, device, or script — that a developer creates in the portal. For OAuth2-secured APIs, an application holds the client ID(s) that link to OAuth applications created directly in a key manager; the portal never generates or stores consumer key/secret pairs.

A developer can have multiple applications, each with independent OAuth2 client IDs. See [Create an Application](manage-applications/create-an-application.md).

!!! note
    Applications are not required for subscriptions or API key generation. Subscriptions are made directly to an API or MCP server, and API keys are bound to an API or MCP server — not to an application.

## Subscription

A **subscription** is a developer's access grant to a specific API or MCP server under a chosen subscription plan. The plan determines the developer's rate limits and quota for that artifact.

Subscriptions are made directly to the artifact — no application is involved. Once subscribed, the developer can invoke it under the terms of the chosen plan. See [Subscribe to an API](manage-subscriptions/subscribe-to-an-api.md).

## API Key

An **API key** is a simple token bound to a specific API or MCP server, used to authenticate requests to artifacts that use API key-based authentication. API keys are generated per artifact — not per application or per subscription.

API keys can be generated, regenerated (rotated), or revoked. Key lifecycle events are published in real time as [webhooks](admin-settings/webhook-integration.md) to your configured subscriber endpoint(s), so whatever system you have listening — typically a handler in front of your API Gateway — can enforce access immediately. See [Manage API Keys](manage-api-keys.md).

## OAuth2 Credentials

For APIs that use OAuth2, developers create an OAuth application directly in a [key manager](admin-settings/key-manager-integration.md), then link the resulting **client ID** to an application in the portal. The portal never sees or stores the client secret — it's supplied by the developer each time they generate an access token, and the portal proxies that token request to the key manager. See [Consume an API Secured with OAuth2](consuming-services/consume-an-api-secured-with-oauth2.md).

## Key Manager

A **key manager** is an external OAuth2 authorization server configured for the organization. Developers create and own their OAuth applications there; the portal only stores a reference to the client ID and proxies `client_credentials` token requests to the key manager's token endpoint. You can configure one or more key managers for the organization. See [Key Manager Integration](admin-settings/key-manager-integration.md).

## Webhook Subscriber

A **webhook subscriber** is an HTTPS endpoint you register to receive real-time event notifications from the portal. When a developer generates an API key or changes a subscription, the portal fires a signed HTTP POST to all matching subscribers; what the subscriber does with that event — for example, propagating the change to an API Gateway — is entirely up to whatever you run behind that endpoint. See [Webhook Integration](admin-settings/webhook-integration.md).
