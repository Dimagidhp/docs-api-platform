---
title: "Configure GitHub Copilot CLI with AI Gateway"
description: "Route GitHub Copilot CLI requests through the AI Gateway using an OpenAI LLM provider and App LLM Proxy to apply guardrails, rate limiting, and analytics."
canonical_url: https://wso2.com/api-platform/docs/guides/ai-and-mcp/ai-coding-assistants/github-copilot-cli-configuration-with-ai-gateway/
md_url: https://wso2.com/api-platform/docs/guides/ai-and-mcp/ai-coding-assistants/github-copilot-cli-configuration-with-ai-gateway.md
tags:
  - guides
  - ai-and-mcp
  - ai-coding-assistants
  - github-copilot
author: WSO2 API Platform Documentation Team
last_updated: 2026-10-01
content_type: "how-to"
---

# Configuring GitHub Copilot CLI with AI Gateway

This guide explains how to configure GitHub Copilot CLI to send requests through WSO2 API Platform using an AI Gateway, an OpenAI LLM provider, and an App LLM Proxy.

By routing requests through WSO2 API Platform instead of invoking OpenAI directly, you can apply security, traffic control, and governance policies such as guardrails, rate limiting, analytics, and monitoring. The Gateway acts as an intermediary, forwarding requests from GitHub Copilot CLI to OpenAI while enforcing these controls.

GitHub Copilot CLI connects to the App LLM Proxy using its bring your own key (BYOK) option, which lets you point it at a model provider of your choice.

---

## Prerequisites

Before you begin, make sure you have the following.

- An [OpenAI API key](https://platform.openai.com/api-keys)
- A WSO2 API Platform admin account
- [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) installed

---

## Step 1: Start an AI Gateway in AI Workspace

!!! note
    If an AI Gateway is already created and active, continue to Step 2.

1. Log in to the **WSO2 API Platform Console**.

2. Create an organization, or select an existing organization from the header at the top of the page.

3. Click **AI Workspace** in the header.

4. In the left navigation panel, click **AI Gateways**.

5. Select an existing gateway, or click **Add AI Gateway** to create one.

6. Follow the instructions shown on the gateway page to download, configure, and start the gateway.

For more information, see [Set up an AI Gateway in AI Workspace](../../../cloud/ai-workspace/ai-gateways/setting-up.md).

Once the gateway status shows as **Active**, continue to Step 2.

[![AI Workspace gateway page showing the gateway as Active and connected successfully](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/github-copilot-cli/ai-gateway-active.png)](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/github-copilot-cli/ai-gateway-active.png)

---

## Step 2: Create and deploy an OpenAI LLM provider

### Create an OpenAI LLM provider

1. In the left navigation panel of AI Workspace, navigate to **LLM → LLM Providers**.

2. Click **Add New Provider**.

3. Select **OpenAI** as the LLM service provider.

4. Enter the required provider details.

5. In the **API Key** field, enter your OpenAI API key.

6. Click **Add Provider**.

### Deploy the OpenAI LLM provider to the AI Gateway

1. On the page that opens after creating the provider, click **Deploy to Gateway**.

2. Find the active AI Gateway where you want to deploy the OpenAI provider.

3. Click **Deploy** next to that gateway.

The OpenAI LLM provider is now deployed to the selected AI Gateway.

---

## Step 3: Create and deploy an App LLM Proxy

The App LLM Proxy is the endpoint that GitHub Copilot CLI invokes through WSO2 API Platform.

1. Click **Back to Service Provider** to return to the OpenAI provider overview page.

2. Click **Create App LLM Proxy**.

3. Select a project. The default project is usually named **Default**.

4. Click **Continue**.

5. Provide a name for the App LLM Proxy.

6. Provide the other required information.

7. Under **Provider Configuration**, select the OpenAI LLM provider you created earlier.

8. Click **Generate API Key**.

9. Provide a name for the API key and generate it.

10. Copy and save the generated API key if required.

11. Provide a unique **Context** for the proxy.

    For example:

    ```text
    /copilotcliproxy
    ```

12. Click **Create Proxy**.

### Configure the API key header for GitHub Copilot CLI

GitHub Copilot CLI sends its API key in the `Authorization` header with a `Bearer` prefix. Configure the App LLM Proxy to read the API key from this header.

1. On the page that opens after creating the proxy, navigate to the **Security** tab.

2. Under **Authentication**, change the **Key name** from `X-API-Key` to `Authorization`.

3. In the **API Key Value Prefix** field, enter `Bearer`.

4. Click **Save**.

### Deploy the App LLM Proxy to the AI Gateway

1. Click **Deploy to Gateway**.

2. Find the active AI Gateway where you deployed the OpenAI LLM provider.

3. Click **Deploy** next to that gateway.

The App LLM Proxy is now deployed to the selected AI Gateway.

### Generate an API key for GitHub Copilot CLI

GitHub Copilot CLI needs an API key from WSO2 API Platform to invoke the deployed App LLM Proxy.

1. Click **Back to App LLM Proxy**.

2. Under **API Keys**, click **Generate API Key**.

3. Provide a name for the API key.

4. Click **Generate**.

5. Copy and save the generated API key.

6. In the **Overview** tab, copy and save the **Invoke URL**.

You use these values when configuring GitHub Copilot CLI.

---

## Step 4: Configure GitHub Copilot CLI to use the App LLM Proxy

GitHub Copilot CLI reads its model provider settings from environment variables.

### Configure environment variables

Open a terminal session where you want to run GitHub Copilot CLI.

Run the following commands, replacing the placeholders with your values.

```bash
export COPILOT_PROVIDER_TYPE="openai"
export COPILOT_PROVIDER_BASE_URL="<INVOKE URL>"
export COPILOT_PROVIDER_API_KEY="<API PLATFORM API KEY>"
export COPILOT_MODEL="gpt-4.1"
```

Replace the placeholders as follows.

- `<INVOKE URL>` with the Invoke URL copied from the App LLM Proxy overview page
- `<API PLATFORM API KEY>` with the API key generated from WSO2 API Platform for the App LLM Proxy

!!! note
    `COPILOT_MODEL` must be an OpenAI model that supports tool calling and streaming. For more information, see [GitHub Copilot CLI's official documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models).

!!! note
    These environment variables apply only to the current terminal session. To make the configuration permanent, add them to your shell profile, such as `~/.zshrc` or `~/.bashrc`.

### Configure SSL certificate trust

When using a local WSO2 API Platform AI Gateway over HTTPS, GitHub Copilot CLI must be able to trust the certificate presented by the Gateway.

!!! note
    If the AI Gateway uses a valid CA-signed certificate, no additional certificate configuration is required.

If the Gateway uses a self-signed certificate, add the Gateway certificate to the certificate trust store used by GitHub Copilot CLI before running the client.

```bash
export NODE_EXTRA_CA_CERTS="<PATH TO GATEWAY CERTIFICATE>"
```

To bypass SSL certificate validation during testing, run the following command.

```bash
export NODE_TLS_REJECT_UNAUTHORIZED=0
```

---

## Step 5: Run GitHub Copilot CLI

After setting the required environment variables, run GitHub Copilot CLI.

```bash
copilot
```

GitHub Copilot CLI sends requests through WSO2 API Platform instead of directly calling OpenAI.

---

## Use case examples

### View API analytics and insights

By routing GitHub Copilot CLI requests through the WSO2 API Platform AI Gateway, you automatically gain access to built-in analytics and reporting capabilities.

WSO2 provides integrated analytics, powered by Moesif, and also supports integration with external tools such as the ELK stack (**Elasticsearch**, **Logstash**, **Kibana**) and Choreo Analytics.

<!-- TODO: Add screenshot of Moesif analytics for GitHub Copilot CLI traffic -->

For more information, see [Integrate with Moesif](https://wso2.com/api-platform/docs/monitoring-and-insights/integrate-bijira-with-moesif/).

---

### Implement AI Gateway guardrails for enhanced control

WSO2 API Platform AI Gateway guardrails enable granular control over the data exchanged between GitHub Copilot CLI and the OpenAI API.

By applying guardrails, you can enforce security and compliance policies such as the following.

- Input validation to ensure prompt integrity
- Output filtering to prevent leakage of sensitive data
- Rate limiting to control API usage and avoid cost overruns

For example, you can configure a **PII Masking Regex Guardrail** in the request flow to prevent Personally Identifiable Information (PII) from reaching the OpenAI API. If a user submits a prompt containing PII, the guardrail evaluates the request against defined patterns and redacts them before they reach the OpenAI API.

<!-- TODO: Add screenshot of GitHub Copilot CLI with PII redacted by the guardrail -->

For more information, see [PII masking regex guardrail](https://wso2.com/api-platform/docs/ai-gateway/llm/guardrails/pii-masking-regex/).

---

### Rate limiting at AI Gateway

WSO2 API Platform AI Gateway supports request-based and token-based rate limiting for AI APIs. This allows you to control GitHub Copilot CLI usage when requests are routed through the Gateway.

For example, you can create an AI subscription policy with a limited request count or total token count, and apply it when subscribing to the App LLM Proxy. Once GitHub Copilot CLI invokes the API through that subscription, the Gateway enforces the selected quota automatically. If the configured limit is exceeded, subsequent requests are throttled until the quota resets.

This helps control token consumption and avoid unexpected costs.

<!-- TODO: Add screenshot of GitHub Copilot CLI after the rate limit is reached -->

For more information, see [Policies overview](https://wso2.com/api-platform/docs/ai-workspace/policies/overview/).

---

### Prompt decorator

WSO2 API Platform AI Gateway supports Prompt Decorators, which allow you to modify or enrich prompts before they are sent to the backend AI provider. This is useful for enforcing consistent instructions, adding system-level context, or guiding model behavior without requiring changes in the client application.

For example, you can configure a Prompt Decorator in the request flow to prepend a system instruction to all incoming prompts.

<!-- TODO: Add screenshots of GitHub Copilot CLI responses without and with the Prompt Decorator -->

For more information, see [Prompt decorator](https://wso2.com/api-platform/docs/ai-gateway/llm/prompt-management/prompt-decorator/).
