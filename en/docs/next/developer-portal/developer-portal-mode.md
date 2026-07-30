---
title: "Developer Portal mode"
description: "Configure the Developer Portal to show APIs only, MCP servers only, or both, using the Developer portal mode field in Organization Settings."
canonical_url: https://wso2.com/api-platform/docs/cloud/devportal/developer-portal-mode/
md_url: https://wso2.com/api-platform/docs/cloud/devportal/developer-portal-mode.md
tags:
  - cloud
  - devportal
  - configuration
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-27
content_type: "concept"
---

# Developer Portal Mode

The Developer Portal can be configured to show APIs only, MCP servers only, or both, depending on your requirements.

This is set via the **Developer portal mode** field on the [Organization Settings](admin-settings/organization-settings.md) tab. Pages for a hidden content type return 404 while that mode is active.

## Modes

| Mode | Value | Behavior |
|---|---|---|
| **APIs and MCP servers** | `DEFAULT` | The default mode. Both APIs and MCP servers are shown in the portal. |
| **APIs only** | `APIS_ONLY` | Only APIs are shown. Suitable if you have nothing to do with MCP. |
| **MCP servers only** | `MCP_SERVERS_ONLY` | Only MCP servers are shown. Suitable if you're using the portal purely for MCP use cases. |

## Change the Mode

1. Log in to the Developer Portal as an admin and navigate to **Settings**.
2. Under the **ORGANIZATION** group, select the **Organization** tab.
3. Under **Developer portal mode**, select **APIs and MCP servers**, **APIs only**, or **MCP servers only**.
4. Click **Save changes**.

You can also set this via the [Management API](rest-api/overview.md) — see `configuration.devportalMode` in [Update an organization](rest-api/organizations.md#update-an-organization).