---
title: "Get started with API Portal & MCP Hub"
description: "Run the API Portal & MCP Hub locally with Docker Compose, sign in, and publish your first API to the catalog."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/getting-started/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/getting-started.md
tags:
  - cloud
  - api-portal
  - quickstart
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-23
content_type: "quickstart"
---

# Getting Started

The API Portal & MCP Hub is where developers discover, subscribe to, and consume the APIs and MCP servers you publish. This guide gets the API Portal & MCP Hub running locally with Docker Compose in a few minutes, then walks you through publishing your first API.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with the Compose plugin (`docker compose version`)
- `openssl` on your `PATH` (used by the setup script to generate certificates and secrets)
- `curl` and `unzip` installed
- Ports **9543** (API Portal & MCP Hub) and **9243** (Platform API) available on your machine

## Step 1: Download the API Portal & MCP Hub

Run this command in your terminal to download and unzip the standalone API Portal distribution:

```bash
curl -sLO https://github.com/wso2/api-platform/releases/download/api-portal%2Fv1.0.0/wso2apip-api-portal-1.0.0-rc.zip && \
unzip wso2apip-api-portal-1.0.0-rc.zip
```

## Step 2: Run the Setup Script

```bash
cd wso2apip-api-portal-1.0.0
./scripts/setup.sh
```

This one-time script provisions everything the containers need to start:

- a self-signed TLS certificate under `resources/certificates/`
- the portal's encryption/session secrets and the shared JWT signing key, written to `api-platform.env`
- the Platform API sidecar config that validates login credentials and issues signed tokens

It also prompts you for an **admin username and password**. Press Enter at the password prompt to have a strong one generated for you — it's printed once at the end, so copy it before continuing.

!!! warning "Save the printed admin credentials"
    The admin password is shown only once and is never stored in plaintext — only its bcrypt hash is written to `api-platform.env`. If you lose it, remove `APIP_CP_ADMIN_USERNAME` and `APIP_CP_ADMIN_PASSWORD_HASH` from `api-platform.env` and rerun `./scripts/setup.sh` to generate a new one.

!!! note "Re-running the script"
    The script is idempotent — re-running it only fills in what's missing and never overwrites an existing value. To rotate a secret, remove it from `api-platform.env` (or delete `resources/certificates/` for the TLS certificate) and re-run.

## Step 3: Start the Portal

```bash
docker compose up -d
```

This starts the API Portal & MCP Hub backed by SQLite by default. On first boot, the database schema and a default organization (`default`) with a `default` view are created automatically.

Verify the Platform API sidecar is healthy:

```bash
curl -fk https://localhost:9243/health
```

## Step 4: Open the Portal

Navigate to:

```
https://localhost:9543/default/views/default
```

You'll see the API Portal home page.

![API Portal home page with the heading "APIs, MCP servers & workflows built for Developers and AI Agents", Browse our APIs, Browse our MCP servers, and Discover with AI buttons, and a Log In button in the top right](../../assets/img/standalone-devportal/getting-started/home-page.png)

Click **Log In** and sign in with the admin username and password from Step 2.

!!! tip "Browser trust warning?"
    The generated TLS certificate is self-signed. Click **Advanced > Proceed** to continue.

You should see the default API catalog page. It stays empty until you add APIs — either seed the bundled samples or publish your own, both covered next.

## Step 5: Seed Sample APIs (Optional)

The fastest way to see a populated catalog is to deploy the bundled sample APIs and MCP servers:

```bash
./scripts/seed-samples.sh
```

This deploys everything under `resources/samples/` into the `default` organization through the public REST API. It prompts for the admin username and password from Step 2 — or set `ADMIN_USERNAME` / `ADMIN_PASSWORD` to skip the prompt. It's safe to re-run: samples that already exist (matched by name and version) are skipped.

!!! note
    Requires `curl`, `jq`, and `zip` on your `PATH`, and the portal must already be running (Step 3).

Refresh the catalog page and the sample APIs appear as a grid of cards, each showing the API's name, version, type, and a **Subscribe** button.

![API Portal API listing page showing a search bar and four sample API cards — Catalog API, Countries GraphQL API, Navigation API, and Reading List API — each with type badges, tags, plan count, and a Subscribe button](../../assets/img/standalone-devportal/getting-started/api-listing-page.png)

To publish an API of your own instead, continue below.

## Step 6: Publish Your First API

Create an API manifest and an OpenAPI definition:

```yaml
# api.yaml
apiVersion: api-portal.api-platform.wso2.com/v1alpha2
kind: RestApi

metadata:
  name: ping-api-v1.0

spec:
  type: REST
  displayName: Ping API
  version: v1.0
  description: Sample HTTP echo/probe API. Requires API key authentication. No subscription plans.
  status: PUBLISHED
  referenceID: ping-api-v1.0

  tags:
    - ping
    - api-key

  labels:
    - default

  subscriptionPlans: []

  visibility: PUBLIC
  visibleGroups: []

  businessInformation:
    businessOwner: Platform Owner
    businessOwnerEmail: support@example.com
    technicalOwner: API Team
    technicalOwnerEmail: architecture@example.com

  endpoints:
    sandboxUrl: http://localhost:8080/ping
    productionUrl: http://localhost:8080/ping
```

```yaml
# openapi.yaml
openapi: 3.0.1
info:
  title: Ping API
  version: 1.0.0
  description: |
    HTTP echo/probe API secured with an API key (`X-API-Key` header).
servers:
  - url: /ping
security:
  - ApiKeyHeader: []
components:
  securitySchemes:
    ApiKeyHeader:
      type: apiKey
      in: header
      name: X-API-Key
  schemas:
    PingResponse:
      type: object
      description: Response returned by the ping/echo service
      additionalProperties: true

paths:
  /get:
    get:
      summary: Echo a GET request
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PingResponse'
```

Then get a bearer token from the Platform API using the admin credentials from Step 2, and publish:

```bash
# Get a token from the Platform API (runs alongside the devportal)
TOKEN=$(curl -sk -X POST "https://localhost:9243/api/portal/v0.9/auth/login" \
  -d "username=<admin-username>&password=<admin-password>" | jq -r .token)

# Publish the API (the token's org_handle claim scopes this to the "default" org)
curl -sk -X POST "https://localhost:9543/api/v0.9/apis" \
  -H "Authorization: Bearer $TOKEN" \
  -F "metadata=@api.yaml;type=application/yaml" \
  -F "definition=@openapi.yaml;type=application/yaml"
```

Refresh the portal — the Ping API now appears in the catalog. Click it to view its documentation and try-out console.

## What's Next

- [Search APIs](discover-apis/api-search.md): find published APIs by name, type, version, or description
- [Create an Application](manage-applications/create-an-application.md): set up a container for OAuth2 credentials
- [Subscribe to an API](manage-subscriptions/subscribe-to-an-api.md): subscribe to a published API under a plan
- [Consume an API Secured with API Key](consuming-services/consume-an-api-secured-with-api-key.md) or [Consume an API Secured with OAuth2](consuming-services/consume-an-api-secured-with-oauth2.md)
- [Theming](admin-settings/theming.md): customize the portal's look and feel
