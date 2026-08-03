---
title: "About this release"
description: "What's included in API Portal & MCP Hub 1.0.0: the API and MCP catalog, API workflows, MCP registry, applications, authentication, theming, and the admin UI."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/about-this-release/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/about-this-release.md
tags:
  - cloud
  - api-portal
  - release-notes
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-03
content_type: "release-notes"
---

# About this release

API Portal & MCP Hub 1.0.0 is the first release of a self-hosted portal for APIs and Model Context Protocol (MCP) servers. API publishers expose APIs and MCP servers, and developers discover, subscribe to, and consume them. Because this is the first release, every capability below is available for the first time.

New to the portal? Start with the [Overview](overview.md), then the [Getting Started](getting-started.md) guide.

## Catalog and discovery

- **API and MCP server catalog:** Browse, document, and consume APIs alongside MCP servers, organized into [views](admin-settings/manage-views.md) with [labels](admin-settings/manage-labels.md). The portal doubles as an MCP Hub, making MCP servers first-class catalog entries next to APIs. See [Discover APIs](discover-apis/api-search.md) and [MCP Servers](mcp-servers/overview.md).
- **API workflows:** Publish multi-step, guided API workflows as a first-class catalog artifact, alongside APIs and MCP servers. See [API Workflows](api-workflows.md).
- **MCP registry:** A programmatic MCP Server Registry API lets agents and tooling discover the MCP servers the portal publishes. See the [MCP Registry API](mcp-servers/mcp-registry.md).
- **AI-ready by design:** MCP-enabled servers pair with `llms.txt` entry points at the portal root and per view. Together, they let artificial intelligence (AI) agents discover the available APIs, MCP servers, and workflows programmatically. See [AI Agent Discovery](discover-apis/ai-agent-discovery.md) and [LLM Instructions](admin-settings/llm-instructions.md).

## Consumption

- **Applications, subscriptions, and API keys:** Consumers create [applications](manage-applications.md), [subscribe to plans](manage-subscriptions.md), and generate and manage [API keys](manage-api-keys.md) and subscription tokens. A browser-based **Try It** console calls APIs directly from the catalog. See [Consume an API](consume-an-api/overview.md).

## Authentication

- **Platform API-backed local authentication:** The built-in login form authenticates against the Platform API sidecar and receives a signed JSON Web Token (JWT).
- **OIDC authentication:** OpenID Connect (OIDC) login runs alongside local authentication, with configurable per-token role-to-scope and group-to-scope mapping. See [Authentication](setting-up/authentication/overview.md).

## Customization

- **Theming:** Customize the portal's colors, styling, logo, and page layouts, and apply custom styling to individual API landing pages. See [Theming](theming.md) and [Apply a Theme](admin-settings/theming.md).
- **Design mode:** A file-based, database-free local preview renders the whole portal—APIs, MCP servers, applications, and theming—straight from sample files on disk. Use it for content authoring and theming without standing up the full stack. See [Design Mode](setting-up/design-mode.md).

## Integration and administration

- **Webhook-based event outbox:** The portal emits signed delivery events for API key, application, and subscription plan changes, so it doesn't depend on a specific gateway or control plane. Receivers react to these events to provision, revoke, or sync resources in downstream systems. See [Webhook Integration](admin-settings/webhook-integration.md) and the [Webhook Event Catalog](references/webhook-event-catalog.md).
- **Admin UI:** A dedicated administrative user interface (UI) manages the organization, views, labels, the API and MCP catalog, API workflows, subscription plans, key managers, and webhook subscribers. See [Admin Settings](admin-settings/organization-settings.md).

## Known issues and limitations

There are no known issues recorded for this release.

## Get started

To install and run the portal, follow the [Getting Started](getting-started.md) guide.
