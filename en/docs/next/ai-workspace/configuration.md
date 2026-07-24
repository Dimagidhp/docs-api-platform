---
title: "AI Workspace Configuration and Environment Interpolation"
description: "How AI Workspace and the Platform API load their config.toml files, inject environment values through interpolation tokens, and bootstrap the keys and certificates the stack requires with the setup script."
canonical_url: https://wso2.com/api-platform/docs/ai-workspace/configuration/
md_url: https://wso2.com/api-platform/docs/ai-workspace/configuration.md
tags:
  - ai-workspace
  - configuration
  - interpolation
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-24
content_type: "reference"
---

# AI Workspace Configuration and Environment Interpolation

The AI Workspace stack - the AI Workspace BFF and the Platform API it proxies to - reads its configuration from TOML files (`config.toml`) layered over built-in defaults. This page explains how configuration is delivered, how environment values are injected through interpolation tokens, and how the one-time setup script provisions the keys and certificates the stack requires.

## How configuration is loaded

Each service reads a TOML file mounted into its container, layered over that service's built-in defaults:

- **AI Workspace (BFF)** - `/etc/ai-workspace/config.toml`; every key lives under the `[ai_workspace]` table.
- **Platform API** - `/etc/platform-api/config.toml`; every key lives under the `[platform_api]` table.

The per-service namespacing (`[ai_workspace]`, `[platform_api]`, `[developer_portal]`) lets one `config.toml` hold multiple services' sections side by side without their keys colliding - each service reads only its own table.

!!! important "Environment variables do not override config keys directly"
    There is **no prefix that auto-maps environment variables onto config keys.** An environment value reaches a setting **only** through an explicit interpolation token written into the config file, resolved when the file is loaded. A key written as a plain literal - or absent from the file - ignores the matching variable entirely.

## Interpolation tokens

Two functions are available inside `config.toml`:

{% raw %}

| Token | Behavior |
|-------|----------|
| `{{ env "NAME" "default" }}` | Substitutes the value of environment variable `NAME`. If the variable is unset **or set-but-empty**, the `default` is used. If no default is given, an unset variable fails startup. |
| `{{ file "PATH" }}` | Reads a secret value from a mounted file at `PATH` - for injecting secrets from a mounted volume rather than an environment variable. A trailing newline is trimmed. |

An example from the shipped AI Workspace `config.toml`:

```toml
[ai_workspace.control_plane]
url = '{{ env "APIP_AIW_CONTROL_PLANE_URL" "https://platform-api:9243" }}'

[ai_workspace.auth]
mode = '{{ env "APIP_AIW_AUTH_MODE" "basic" }}'
```

{% endraw %}

Every token in the shipped config carries a default, so an unset variable keeps the built-in value.

!!! note "The token argument is a naming convention, not a prefix override"
    By convention each token names the key's dotted path (the table segment and key, uppercased, dots as underscores), prefixed per service: **`APIP_AIW_`** for AI Workspace (so `[ai_workspace.control_plane] url` → `APIP_AIW_CONTROL_PLANE_URL`), **`APIP_CP_`** for the Platform API, and **`APIP_DP_`** for the Developer Portal. This is purely the literal string passed to the interpolation function - not a prefix the loader interprets - so renaming the variable also requires editing the matching token in the config file.

### Common tokens

The shipped config files already carry interpolation tokens for the settings the sample deployments inject. The most common are:

| Environment variable (token argument) | Config key | Description |
|----------------------------------------|------------|-------------|
| `APIP_AIW_CONTROL_PLANE_URL` | `ai_workspace.control_plane.url` | Absolute URL the BFF uses to reach the Platform API (e.g. `https://platform-api:9243`) |
| `APIP_AIW_AUTH_MODE` | `ai_workspace.auth.mode` | `basic` (file-based local auth) or `oidc` (external IDP) |
| `APIP_AIW_AUTH_OIDC_CLIENT_ID` / `..._CLIENT_SECRET` | `ai_workspace.auth.oidc.*` | OIDC confidential-client credentials (only in `oidc` mode) |
| `APIP_AIW_LOGGING_LEVEL` | `ai_workspace.logging.level` | `debug`, `info`, `warn`, `error` |
| `APIP_CP_ADMIN_USERNAME` | `platform_api.auth.file.users[].username` | Basic-auth admin username |
| `APIP_CP_ADMIN_PASSWORD_HASH` | `platform_api.auth.file.users[].password_hash` | **bcrypt** hash of the admin password |
| `APIP_CP_LOGGING_LEVEL` | `platform_api.logging.level` | `debug`, `info`, `warn`, `error` |

For the complete list of tokens and every configurable option, refer to the config templates: [AI Workspace](https://github.com/wso2/api-platform/blob/main/portals/ai-workspace/configs/config-template.toml) and [Platform API](https://github.com/wso2/api-platform/blob/main/platform-api/config/config-template.toml).

## Secrets

Never write a secret as a literal in `config.toml`, and never hardcode one in `docker-compose.yaml`. Reference each with an interpolation token - from an environment variable or, preferably, from a mounted file:

{% raw %}

```toml
# Platform API at-rest encryption key - the shipped default reads a mounted file:
encryption_key = '{{ file "/etc/platform-api/keys/encryption.key" }}'
# or, alternatively, from an environment variable:
# encryption_key = '{{ env "APIP_CP_ENCRYPTION_KEY" }}'

# AI Workspace OIDC client secret (oidc mode) - env var, or a mounted file:
client_secret = '{{ env "APIP_AIW_AUTH_OIDC_CLIENT_SECRET" }}'
# client_secret = '{{ file "/secrets/ai-workspace/oidc_client_secret" }}'
```

{% endraw %}

Both forms fail closed: if the variable is unset/empty, or the file is missing or outside the allowed source directories, the service refuses to start. A {% raw %}`{{ file }}`{% endraw %} path must live under an allowed directory - `/etc/ai-workspace` or `/secrets/ai-workspace` for the BFF, `/etc/platform-api` or `/secrets/platform-api` for the Platform API. Override the list with the shared `APIP_CONFIG_FILE_SOURCE_ALLOWLIST` (comma-separated; it **replaces** the defaults rather than extending them).

!!! tip "Distinct from AI Workspace secrets"
    The interpolation tokens described here configure the **services' own `config.toml`**. They are unrelated to the **AI Workspace secrets** feature - the encrypted credentials you store and reference in artifacts with {% raw %}`{{ secret "handle" }}`{% endraw %}. See [Secrets Management](./secrets-management.md) for that mechanism.

## Delivering environment values

For Docker Compose deployments, the sample compose delivers these values from a git-ignored `api-platform.env` via the `env_file:` directive. It uses `format: raw` so a bcrypt password hash's `$` characters are not treated as Compose interpolation:

```yaml
services:
  platform-api:
    env_file:
      - path: api-platform.env
        required: true
        format: raw
```

`api-platform.env` is generated by the [setup script](#one-time-setup-with-setupsh). Add or edit variables there - for example, to switch the AI Workspace login mode or point at a different control plane.

The stack **never auto-generates keys or certificates** and fails closed with a descriptive error at startup if a required secret is missing. Everything must be provisioned before the first start:

- **TLS certificate** - the HTTPS certificate/key for the AI Workspace and Platform API listeners.
- **RS256 JWT signing keypair** - the Platform API signs login tokens with the private key; the AI Workspace and Developer Portal verify them with the public key. There is no shared HMAC secret.
- **At-rest encryption key** - the Platform API's 32-byte key for encrypting stored secrets, subscription tokens, and WebSub HMAC secrets at rest.
- **Admin credentials** - the Platform API's basic-auth admin user.

The setup script provisions all of these.

## One-time setup with `setup.sh`

The distribution ships `setup.sh`, which provisions everything a fresh stack needs. Run it once before the first `docker compose up`:

```bash
./setup.sh
docker compose up -d
```

`setup.sh` provisions, idempotently (existing files are kept unless `--force`):

| Artifact | Location | Purpose |
|----------|----------|---------|
| TLS certificate | `resources/certificates/cert.pem` + `key.pem` | Self-signed HTTPS pair shared by the services (mounted at `/etc/ai-workspace/tls`, `/etc/platform-api` cert paths). |
| RS256 JWT keypair | `resources/keys/jwt_private.pem` + `jwt_public.pem` | Signs/verifies login JWTs; read by `config.toml` via a `file` token. |
| At-rest encryption key | `resources/keys/encryption.key` | Platform API at-rest encryption key (32 bytes, 64 hex chars); read via a `file` token. **Retain it** - losing or changing it makes previously-encrypted secrets unreadable. |
| Admin credentials | `api-platform.env` | Platform API basic-auth credential (`APIP_CP_ADMIN_USERNAME` + bcrypt `APIP_CP_ADMIN_PASSWORD_HASH`). |

!!! note "Admin credentials"
    The Platform API login is protected by basic auth. You provide the plaintext `ADMIN_USERNAME` (defaults to `admin`) and `ADMIN_PASSWORD` (used if set, otherwise prompted, otherwise randomly generated) to `setup.sh`; it writes `APIP_CP_ADMIN_USERNAME` and the **bcrypt** `APIP_CP_ADMIN_PASSWORD_HASH` into `api-platform.env` and prints the plaintext password **once** - copy it. For non-interactive use: `ADMIN_USERNAME=admin ADMIN_PASSWORD='…' ./setup.sh`.

The script is **idempotent** - existing files are kept, not overwritten. Flags:

| Flag | Effect |
|------|--------|
| `--force` | Regenerate the certificate, JWT keypair, and encryption key (rotating them) and re-provision the admin credentials (rotating the password). |
| `--certs-only` | Generate only the TLS certificate; skip the JWT keypair, encryption key, admin credentials, and `api-platform.env`. |

!!! warning "Rotating the encryption key"
    Running `setup.sh --force` regenerates the at-rest encryption key. Data encrypted with the previous key becomes unreadable, and rotating the JWT keypair invalidates issued login tokens. Only rotate deliberately.

---

[← Getting Started](./getting-started.md) &nbsp;|&nbsp; [Secrets Management →](./secrets-management.md)
