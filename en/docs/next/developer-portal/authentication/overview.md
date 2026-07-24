---
title: "Authentication in the Developer Portal"
description: "Understand the two ways users sign in to the Developer Portal: local authentication against the Platform API for development, and an OIDC identity provider for production."
canonical_url: https://wso2.com/api-platform/docs/cloud/devportal/authentication/overview/
md_url: https://wso2.com/api-platform/docs/cloud/devportal/authentication/overview.md
tags:
  - cloud
  - devportal
  - authentication
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-24
content_type: "concept"
---

# Authentication in the Developer Portal

The Developer Portal reads its settings from a single `config.toml` file, under the `[developer_portal.*]` tables. Authentication is controlled by `mode` in the `[developer_portal.auth]` table, which selects between two backends. A running instance uses one mode at a time.

| Mode | `[developer_portal.auth] mode` | Best for |
|------|-------------------------------|----------|
| Local | `local` | Development and local testing, no identity provider required |
| Identity provider | `idp` | Production, where a dedicated OIDC identity provider manages user login |

The block matching your chosen mode is used; the other is ignored.

## Login flow

The two modes present users with different login experiences:

- **Local mode** (`mode = "local"`): clicking **Login** on any portal page shows a built-in username and password form. Credentials are validated against the Platform API.

- **Identity provider mode** (`mode = "idp"`): clicking **Login** redirects the user directly to the identity provider's authorization endpoint — no intermediate login page is shown. After authenticating, the user is returned to the page they originally requested.

Public pages (the API catalog and documentation) are always accessible without authentication in either mode. Only protected pages — applications, subscriptions, and API keys — require login.

## Local authentication

Local authentication delegates credential validation to the Platform API control plane. It requires no external identity provider, which makes it the default for local development and quick trials.

When `[developer_portal.auth] mode = "local"`, the portal renders a username and password form and validates the credentials against the Platform API. Users, bcrypt-hashed passwords, and scopes are defined in the Platform API's own configuration, under `[[platform_api.auth.file.users]]`.

```toml
[developer_portal.auth]
mode = "local"

[developer_portal.auth.local]
# The upstream Platform API used to validate credentials.
platform_api_url = "https://platform-api:9243"
# Path to the Platform API's RS256 public key PEM — the matching half of its
# [platform_api.auth.jwt] private key. Bearer-token requests fail closed without it.
public_key_path  = "/etc/devportal/keys/jwt_public.pem"
tls_skip_verify  = false
```

Leave `platform_api_url` empty to disable local authentication entirely.

Local authentication is intended for development and local testing only. Move to an identity provider before deploying to a shared or production environment.

## Identity provider authentication

For production, configure the portal to delegate login to an identity provider (IdP) over OIDC. The Developer Portal works with any OIDC-compliant IdP — such as Asgardeo, Keycloak, Auth0, or Okta — that meets these requirements:

| Requirement | Details |
|-------------|---------|
| OIDC endpoints | The IdP exposes authorization, token, and (optionally) userinfo endpoints, discoverable from its `/.well-known/openid-configuration` |
| JWT access tokens | Access tokens are JWTs, not opaque tokens |
| Signature verification | The IdP exposes a JWKS endpoint, or you supply its X.509 certificate, so the portal can verify token signatures |
| Confidential client | The portal is registered as a confidential client with a client secret (a server-side Traditional Web Application), not a public single-page application |
| Claims | Tokens carry the organization identifier and the user's roles as claims (claim names are configurable) |

When `mode = "idp"`, the portal reads the `[developer_portal.auth.idp]` block for the OIDC endpoints and client credentials, and the `[developer_portal.auth.claim_mappings]` block for the claim names that carry organization and role information.

!!! note
    We're expanding our step-by-step setup guides to cover more identity providers. For now, [Set up Asgardeo as your identity provider](asgardeo-setup.md) walks through a complete configuration using WSO2 Asgardeo. The same concepts apply to any OIDC-compliant IdP.

## Choosing a mode

Use local authentication when you're trying out the Developer Portal, running a demo, or don't yet have an identity provider available. Move to an identity provider before you deploy to a shared or production environment, need to serve multiple organizations, or want single sign-on with an existing identity system.
