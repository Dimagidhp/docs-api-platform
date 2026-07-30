---
title: "View the API overview page in the Developer Portal"
description: "See an API's version, description, tags, endpoints, resources, and subscription plans on its overview page before subscribing or trying it out."
canonical_url: https://wso2.com/api-platform/docs/cloud/devportal/discover-apis/api-overview/
md_url: https://wso2.com/api-platform/docs/cloud/devportal/discover-apis/api-overview.md
tags:
  - cloud
  - devportal
  - discover-apis
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-27
content_type: "how-to"
---

# API Overview

Every API's overview page shows a summary of what the API does, how to reach it, and how to start consuming it, before you dig into the full [documentation](api-documentations.md).

## View an API's Overview Page

1. Go to **APIs** in the sidebar and [search or browse](api-search.md) for the API you want.
2. Click the API's card to open it. The overview page loads by default.

    ![Catalog API overview page showing the API header with version and type badges, description, tags, Subscribe/Documentation/Try with AI/API Keys buttons, Production and Sandbox endpoint URLs, a Resources list of GET endpoints, and a Subscription plans panel with Gold and Bronze tiers](../../../assets/img/standalone-devportal/discover-apis/api-overview/api-overview.png)

## What You'll Find

The header shows the API's metadata such as icon, name, version, and description, along with tags (informational only, not clickable filters) and the following badges:

- **Type**: the API type (REST, GraphQL, WebSocket, SOAP, or WebSub)
- **AI Ready**: shown when the API exposes agent-friendly documentation
- **Deprecated**: shown if the API has been deprecated

### Action Buttons

- **Subscribe**: jumps down to the subscription plans. Only shown if the API has plans and you're not already subscribed to one
- **Documentation**: opens the API's full documentation. Not shown for SOAP APIs, which show a **Download** button for the WSDL file instead
- **Try with AI**: opens a modal with a ready-made prompt (plus a **Run in Claude** shortcut) that briefs an AI agent on the API using its machine-readable documentation. Only shown if the API is agent-visible
- **API Keys**: opens the API Keys page to generate a key. Only shown for APIs secured with API key authentication

### Page Sections

- **Endpoints**: the Production and Sandbox base URLs, each with a copy button
- **Resources**: for REST APIs, every operation with its HTTP method, path, and summary. GraphQL APIs show only the Endpoints section; WebSocket and WebSub APIs show a **Channels** section (with PUB/SUB badges) instead of Resources
- **Subscription plans**: the plans available for this API (e.g. Gold, Bronze) and their rate limits. Click **Subscribe** on a plan to generate a subscription if you're already subscribed, this becomes **View subscription** instead

!!! note
    MCP servers have their own overview page with a similar layout, but it shows the server's Tools, Resources, and Prompts instead of REST-style resources, and an MCP Server Configuration snippet instead of a plain endpoint list.

## Related

- [Search APIs](api-search.md): find the API you want to open
- [API Documentation](api-documentations.md): full endpoint, schema, and security details
- [Subscribe to an API](../manage-subscriptions/subscribe-to-an-api.md)
- [Manage API Keys](../manage-api-keys.md)
