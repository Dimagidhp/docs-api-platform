---
title: "Get started with AI Workspace"
description: "Run AI Workspace locally with Docker Compose, create an AI Gateway, configure an LLM provider, and deploy it through the AI Workspace control plane."
canonical_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/getting-started/
md_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/getting-started.md
tags:
  - cloud
  - ai-workspace
  - quickstart
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-31
content_type: "quickstart"
---

# Getting Started

The AI Workspace enables you to manage AI gateways and LLM providers. This guide gets AI Workspace running locally with Docker Compose, then walks you through creating your first AI gateway and LLM provider.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with the Compose plugin (`docker compose version`)
- Ports **9643** and **9243** available on your machine. If either one is taken, see [Change the ports the stack uses](ports.md).
- `curl` and `unzip` installed

## Step 1: Download AI Workspace

Run this command in your terminal to download and unzip AI Workspace:

```bash
curl -sLO https://github.com/wso2/api-platform/releases/download/portals/ai-workspace/v1.0.0-rc/wso2apip-ai-workspace-1.0.0-rc.zip && \
unzip wso2apip-ai-workspace-1.0.0.zip
```

## Step 2: Run the Setup Script

```bash
cd wso2apip-ai-workspace-1.0.0
./scripts/setup.sh
```

Run the script once before the first start. The stack never auto-generates keys or certificates: every service fails closed with a descriptive error if something it needs is missing, rather than starting with a weaker value. The script prompts for the admin username and password — press <kbd>Enter</kbd> at each prompt to accept `admin` and a randomly generated password — and provisions the following:

| Artifact | Location | Purpose |
|----------|----------|---------|
| TLS certificate | `resources/certificates/cert.pem` and `key.pem` | Self-signed HTTPS pair shared by the services. |
| RS256 JWT signing keypair | `resources/keys/jwt_private.pem` and `jwt_public.pem` | The Platform API signs login tokens with the private key; AI Workspace and the API Portal verify them with the public key. There's no shared HMAC secret. |
| At-rest encryption key | `resources/keys/encryption.key` | The Platform API's 32-byte key for encrypting stored secrets, subscription tokens, and WebSub HMAC secrets. **Retain it** — losing or changing it makes previously-encrypted data unreadable. |
| API Portal encryption key | `resources/keys/api-portal-encryption.key` | Encrypts the API Portal's subscription and webhook secrets at rest. Retain it for the same reason. |
| API Portal session secret | `resources/keys/api-portal-session-secret` | Signs API Portal session cookies. Rotating it only signs users out. |
| Admin credentials | `api-platform.env` | The Platform API's basic-auth admin user: `APIP_CP_ADMIN_USERNAME` plus the bcrypt `APIP_CP_ADMIN_PASSWORD_HASH`. |
| Compose defaults | `.env` | `COMPOSE_PROFILES`, which decides the services a plain `docker compose up -d` starts, and `COMPOSE_PROJECT_NAME`, which namespaces this copy's containers, networks, and volumes. |

To skip both prompts — in CI, for example — set the credentials in the environment instead: `ADMIN_USERNAME=admin ADMIN_PASSWORD='…' ./scripts/setup.sh`.

!!! warning "Save the printed admin username and password"
    The admin password is shown only once, and `api-platform.env` holds only its bcrypt hash. To set a new one, delete both `APIP_CP_ADMIN_USERNAME` and `APIP_CP_ADMIN_PASSWORD_HASH` from `api-platform.env` and rerun `./scripts/setup.sh`. Deleting only one of the two makes the script stop with an error, because a username without its matching hash can never authenticate.

!!! warning "Don't delete or edit `COMPOSE_PROJECT_NAME`"
    The project name is pinned on the first run and never changes afterwards — not on a rerun, not under any flag. The stack's data lives in volumes prefixed with it, so a different name starts the stack with an empty database. To choose the name yourself, set `COMPOSE_PROJECT_NAME` in the environment for the first run.

## Step 3: Start the Stack

```bash
docker compose up -d
```

!!! tip "Port 9643 or 9243 already taken?"
    Change the host side of the `ports:` mappings in `docker-compose.yaml` before you start — for example `"8443:9643"` for the AI Workspace. See [Change the ports the stack uses](ports.md) for the two config keys that need to match.

## Step 4: Open AI Workspace

Open `https://localhost:9643` and sign in with the admin credentials that `setup.sh` printed:

![AI Workspace file-based login window with Username and Password fields](../../assets/img/ai-gateway/standalone-ai-workspace/authentication/filebased-login.png)

!!! tip "Browser trust warning?"
    The generated TLS certificates are self-signed. Click **Advanced > Proceed** to continue, then return to the workspace.

!!! note "About this login"
    These credentials come from file-based authentication, generated by the setup script and stored in your local environment configuration. Use them to try AI Workspace locally. Before you move to a production or shared environment, connect an identity provider to manage user login. See [Authentication in AI Workspace](authentication/overview.md).

## Step 5: Create an AI Gateway

An AI gateway is the runtime that processes and routes requests between your applications and LLM providers. You need at least one gateway before configuring providers or proxies.

1. Navigate to **AI Gateways** in the left navigation menu.
2. Click **+ Add AI Gateway**.
3. Fill in the **Name** and **URL**, then click **Add Gateway**.
4. Copy the **Gateway Registration Token** and save it securely immediately — it is shown only once. Then follow the setup instructions to start the gateway runtime.
5. Once connected, the gateway status changes from **Inactive** to **Active**.

For detailed instructions, see [AI Gateways](ai-gateways/setting-up.md).

## Step 6: Configure an LLM Provider

An LLM provider connects AI Workspace to an AI service platform such as OpenAI, Anthropic, or Azure OpenAI.

1. Navigate to **LLM** > **Service Provider**.
2. Click **+ Add New Provider** and select your provider type.
3. Fill in the **Name**, **Version**, and **API Key**, then click **Add Provider**.
4. Configure how applications authenticate when they access this provider through the gateway.
5. Click **Deploy to Gateway** and select your active gateway.

For detailed instructions, see [Configure LLM provider](llm-providers/configure-provider.md).

## Rerun the setup script

Rerunning `./scripts/setup.sh` is safe. By default it fills in only what's missing and never overwrites a value that already exists. The flags change that:

| Flag | Effect |
|------|--------|
| `--force` | Regenerate the TLS certificate, the JWT keypair, and the API Portal session secret, and rotate the admin credentials. Never touches either encryption key. |
| `--rotate-encryption-key` | Replace `resources/keys/encryption.key` and `resources/keys/api-portal-encryption.key`, even though they exist. Destructive — see the warning below. |
| `--certs-only` | Generate only the TLS certificate. Skips the keys, the admin credentials, and `api-platform.env`. |
| `--profiles=<a,b,...>` | Write a different `COMPOSE_PROFILES` value to `.env`, for example `--profiles=all` or `--profiles=platform-api`. |

To rotate a single value by hand, delete it from `api-platform.env` — or delete the file under `resources/certificates` or `resources/keys` — and rerun the script.

!!! warning "Rotating an encryption key destroys encrypted data"
    `--rotate-encryption-key` makes everything encrypted under the old key permanently unreadable, including stored [AI Workspace secrets](secrets-management.md). At an interactive terminal the script asks you to type `rotate` to confirm; in a non-interactive run, passing the flag is itself the confirmation. Rotating the JWT keypair with `--force` is milder — it only invalidates issued login tokens, so everyone signs in again.

## Provision the at-rest encryption key manually

If you don't run `setup.sh`, provision the at-rest encryption key yourself before the first start. It protects [AI Workspace secrets](secrets-management.md), subscription tokens, and WebSub HMAC secrets, and the Platform API refuses to start if it's missing or malformed. Keep it stable across restarts and replicas.

The key is a single 32-byte AES-256 value, supplied as 64 hex characters or base64. Generate it and write it to the file the container mounts at `/etc/platform-api/keys`:

```sh
openssl rand -hex 32 > resources/keys/encryption.key
```

A trailing newline is trimmed on load. The Platform API doesn't read the key from an environment variable directly. It reads the `encryption_key` field in `config.toml`, which pulls the value in through an interpolation token:

{% raw %}
```toml
# config.toml - resolved from a mounted key file:
encryption_key = '{{ file "/etc/platform-api/keys/encryption.key" }}'

# Alternatively, from an environment variable:
# encryption_key = '{{ env "APIP_CP_ENCRYPTION_KEY" }}'
```
{% endraw %}

To use the environment variable form instead, switch the token to {% raw %}`{{ env "APIP_CP_ENCRYPTION_KEY" }}`{% endraw %} and set the variable in `api-platform.env`. For how these tokens work, see [AI Workspace configuration and environment interpolation](configuration.md).

## Change environment values after setup

`api-platform.env` holds the values the containers read at startup — the admin credentials the setup script wrote, and anything else your `config.toml` pulls in through an {% raw %}`{{ env }}`{% endraw %} token. Edit that file to change a setting, for example to switch the AI Workspace login mode or point at a different control plane, then restart the stack.

The sample `docker-compose.yaml` loads the file with the `env_file:` directive. It sets `format: raw` so that the `$` characters in a bcrypt password hash aren't treated as Compose interpolation:

```yaml
services:
  platform-api:
    env_file:
      - path: api-platform.env
        required: true
        format: raw
```

Keep `api-platform.env` out of source control. It's git-ignored in the distribution.

## What's Next

- [Manage your provider](llm-providers/manage-provider.md): configure connection, access control, security, rate limiting, guardrails, and models

!!! note
    Create an App LLM proxy only when a specific GenAI application or agent needs its own guardrails, authentication, exposed resources, or routing on top of a provider.

- [Configure App LLM proxy](llm-proxies/configure-proxy.md): create a specialized endpoint only when you need app-specific or agent-specific controls on top of a provider
- [Manage your App LLM proxy](llm-proxies/manage-proxy.md): configure provider settings, resources, security, and guardrails

