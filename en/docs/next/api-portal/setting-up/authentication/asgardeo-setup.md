---
title: "Set up Asgardeo as your identity provider"
description: "Configure WSO2 Asgardeo as the OIDC identity provider for a production API Portal deployment, from application registration to config.toml."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/setting-up/authentication/asgardeo-setup/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/setting-up/authentication/asgardeo-setup.md
tags:
  - cloud
  - api-portal
  - authentication
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-24
content_type: "how-to"
---

# Set up Asgardeo as your identity provider

This guide walks you through configuring WSO2 Asgardeo as the identity provider for a production API Portal deployment. For background on how identity provider authentication works, see [Authentication in the API Portal & MCP Hub](overview.md).

The API Portal & MCP Hub uses Asgardeo's sub-organization model: each API Portal organization maps to one Asgardeo sub-organization. A single Asgardeo application, shared across all portal organizations, handles login, but each session is scoped to a specific sub-organization:

1. A portal organization has its `idpRefId` set to its Asgardeo sub-org handle.
2. When a user clicks **Login**, the portal redirects to Asgardeo with `org=<identifier>`, scoping the authorization to that sub-organization.
3. Asgardeo issues a JWT whose organization claim identifies the sub-organization. On every authenticated request, the portal verifies this claim matches the organization being accessed.
4. Each session is bound to one sub-organization—accessing a different portal organization's protected pages requires logging out and back in on that organization.

## Prerequisites

- An Asgardeo account at [console.asgardeo.io](https://console.asgardeo.io)
- The API Portal & MCP Hub accessible at a known hostname
- The [`register_asgardeo_scopes.sh`](https://github.com/wso2/api-platform/blob/main/portals/api-portal/production/scripts/register_asgardeo_scopes.sh) helper script, downloaded from the WSO2 API Platform GitHub repository

## Step 1: Set up your organization

1. Log in to [console.asgardeo.io](https://console.asgardeo.io).
2. Create or select your root organization.
3. If you need multiple tenants, create sub-organizations at `https://console.asgardeo.io/t/<root-org>/app/organizations`.

## Step 2: Register the API Portal application

The API Portal & MCP Hub is a server-side application that can hold a client secret, so register it as a confidential client. A single-page application is a public client and cannot complete the confidential authorization-code exchange the portal relies on.

1. In the root organization, go to **Applications > New Application**.
2. Choose **Traditional Web Application** and name it `API Portal & MCP Hub`.
3. Under **Authorized redirect URLs**, add both:
      - `https://<your-domain>/default/callback`—the login callback
      - `https://<your-domain>/default`—the post-logout redirect (Asgardeo validates `post_logout_redirect_uri` against this same list)

    This single shared URI pair is the only one you register. It matches the `callback_url` and `logout_redirect_uri` you set in step 5—after the callback, the portal uses the session's stored return path to route the user to the correct organization, so no per-organization redirect URLs are needed.
4. Enable **Share with all organizations** so users in sub-organizations can log in.
5. Under the **Protocol** tab, set **Access Token Type** to **JWT**.
6. Under the **Login Flow** tab, remove the Username/Password authenticator and add **SSO Authentication** (organization SSO), which routes each user to their sub-organization's login experience.
7. Under the **User Attributes** tab, add these attributes to the token: `given_name`, `family_name`, `email`, and `roles`.

Note the client ID and client secret from the **Protocol** tab. The portal needs both, and the client ID is also used as the audience in the portal configuration.

## Step 3: Register the `dp:*` scopes

The API Portal & MCP Hub enforces `dp:*` scopes per operation for machine API clients that call `/api/v0.9/*` directly with a Bearer token. Register these scopes in Asgardeo using a dedicated system application before assigning them to users.

1. Create a new OIDC application, for example named `DevPortal System`.
2. Under **API Authorization**, add the **API Resource Management API** and the **Application Management API**.
3. Note the client ID and client secret.
4. Download the scope registration script and run it:

```bash
curl -sLO https://raw.githubusercontent.com/wso2/api-platform/main/portals/api-portal/production/scripts/register_asgardeo_scopes.sh
chmod +x register_asgardeo_scopes.sh

ASGARDEO_TENANT=<your-tenant> \
ASGARDEO_CLIENT_ID=<system-app-client-id> \
ASGARDEO_CLIENT_SECRET=<system-app-client-secret> \
ASGARDEO_RESOURCE_IDENTIFIER=https://<your-domain> \
./register_asgardeo_scopes.sh
```

This registers an API resource in Asgardeo that represents the API Portal & MCP Hub, with all `dp:*` scopes registered under it. For local testing, the default `ASGARDEO_RESOURCE_IDENTIFIER=https://localhost:9543` works without changes.

The system application is only needed to run this script. Once the `dp:*` API resource is registered, the system application can be deleted.

!!! note
    Browser login sessions are preauthorized—the portal trusts session-level authentication and skips per-operation scope checks for users signed in through the IdP. The `dp:*` scopes matter only for machine clients calling the REST API directly with a Bearer token, which is why `scope` in the configuration below does not need to request them.

## Step 4: Link the scopes to the application

1. Open the **API Portal & MCP Hub** application you registered in step 2.
2. Under **API Authorization**, add the API resource created in step 3.
3. Create an **admin** application role and assign all `dp:*` scopes to it. The role's name must match the value the portal maps to its `admin` tier in `[api_portal.auth.authorization.portal_roles]`—`admin`, per the mapping in step 5. Assign this full-scope role **only to administrators**.
4. Create a separate least-privilege role for regular subscribers, granting only the `dp:*` scopes needed for everyday subscriber operations—for example `dp:application:manage` and `dp:subscription:manage` to manage applications and subscriptions, plus the `dp:*:read` scopes for browsing APIs. Name it to match the value mapped to the portal's `subscriber` role (`Internal/subscriber` below).
5. Assign the admin role to administrators only, and the subscriber role to regular users in each sub-organization that needs access.

## Step 5: Configure the API Portal & MCP Hub

Update the `[api_portal.auth]` tables in `configs/config.toml`:

{% raw %}
```toml
[api_portal.auth]
mode = "idp"

[api_portal.auth.idp]
name              = "Asgardeo"
issuer            = "https://api.asgardeo.io/t/<your-tenant>/oauth2/token"
authorization_url = "https://api.asgardeo.io/t/<your-tenant>/oauth2/authorize"
token_url         = "https://api.asgardeo.io/t/<your-tenant>/oauth2/token"
user_info_url     = "https://api.asgardeo.io/t/<your-tenant>/oauth2/userinfo"
jwks_url          = "https://api.asgardeo.io/t/<your-tenant>/oauth2/jwks"
client_id         = "<api-portal-app-client-id>"
client_secret     = '{{ env "APIP_AP_AUTH_IDP_CLIENT_SECRET" }}'
audience          = "<api-portal-app-client-id>"   # Asgardeo sets the client ID as the aud claim
callback_url      = "https://<your-domain>/default/callback"
logout_url        = "https://api.asgardeo.io/t/<your-tenant>/oidc/logout"
logout_redirect_uri = "https://<your-domain>/default"
scope             = "openid profile email roles"

# Which token claim carries each field. Asgardeo B2B puts the sub-org handle in org_name.
[api_portal.auth.claim_mappings]
organization = "org_name"
roles        = "roles"

# Maps Asgardeo role values to the portal's two page-access tiers. This section is
# mode-independent — it is NOT under [api_portal.auth.idp].
[api_portal.auth.authorization]
mode = "role"

[api_portal.auth.authorization.portal_roles]
admin      = "admin"
subscriber = "Internal/subscriber"
```
{% endraw %}

`mode = "idp"` selects the identity provider backend and stops the local login form from being used. `callback_url` must exactly match one of the authorized redirect URLs you registered in step 2. A single `callback_url` is shared across all portal organizations—after the callback, the portal uses the session's stored return path to redirect the user to the correct organization, so you register only this one URL with Asgardeo.

Never write the client secret as a literal in `config.toml`—the {% raw %}`{{ env }}`{% endraw %} placeholder above reads it from an environment variable instead, so it never has to be committed to source control:

```bash
export APIP_AP_AUTH_IDP_CLIENT_SECRET=<api-portal-app-client-secret>
```

In a production deployment, prefer supplying it from a mounted secret file instead, by swapping the token for {% raw %}`'{{ file "/secrets/api-portal/oidc_client_secret" }}'`{% endraw %} and mounting the secret at that path—resolution fails closed, so a missing or unreadable file aborts startup rather than falling back to an empty credential.

## Step 6: Map organizations to sub-organizations

Each API Portal organization maps to one Asgardeo sub-organization. To enable org-scoped login and access isolation, set the organization's `idpRefId` field (managed through the API Portal's Organization admin API) to the Asgardeo sub-org's **handle** (the URL slug shown in the Asgardeo console).

When a user clicks **Login**, the portal appends `org=<idpRefId>` to the Asgardeo authorization URL. Asgardeo scopes the login session to that sub-organization and issues a token whose organization claim identifies it. On every authenticated request, the portal verifies that the token's organization claim matches the organization's `idpRefId`; a mismatch blocks access to protected pages with a 403, and the user must log out and log in again on the correct organization.

- One login session per organization—each session is scoped to one Asgardeo sub-organization.
- Public pages (the API catalog and documentation) remain accessible across organizations without re-authentication.
- Protected pages (applications, subscriptions, API keys) require a token matching the organization's `idpRefId`.

Once configured, opening the API Portal and clicking **Login** redirects you to the Asgardeo-hosted login page instead of the built-in local login form:

## Claim flow summary

The Asgardeo token carries these claims through to the API Portal & MCP Hub:

| Claim | Purpose | Configured as |
|-------|---------|----------------|
| `sub` | User identity | N/A |
| `org_name` | Sub-organization handle, compared against the organization's `idpRefId` | `organization` in `[api_portal.auth.claim_mappings]` |
| `roles` | Role list, used for the admin check and, in `mode = "role"`, expanded into Management API scopes | `roles` in `[api_portal.auth.claim_mappings]`, mapped by `[api_portal.auth.authorization.portal_roles]` |

Keep the claim names consistent between the Asgardeo token attributes and the `[api_portal.auth.claim_mappings]` table.

!!! important "Two retired keys abort startup"
    Earlier versions configured roles under `[api_portal.auth.idp.roles]`, with a third `super_admin` tier. That section is retired, along with `auth.role_validation`, and leaving either in `config.toml` fails startup rather than silently applying a default. Use `[api_portal.auth.authorization.portal_roles]` and `auth.authorization.page_role_validation` instead—see [Authorization](../../references/configurations.md#authorization).

## Granting management API access

With `mode = "role"` (the default), a token's `roles` claim is expanded into `dp:*` scopes through the grant table at `auth.authorization.role_to_scope_mapping`, and the token's own scope claim is ignored. That's why step 3's Asgardeo role name has to match a role in that table.

If you'd rather have Asgardeo mint `dp:*` scopes directly, run `production/scripts/register_asgardeo_scopes.sh` against your tenant to register them, then set `mode = "scope"` so the portal reads the scope claim instead.

