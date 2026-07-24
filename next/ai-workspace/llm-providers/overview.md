---
title: "LLM providers overview"
description: "Connect AI service platforms such as OpenAI, Anthropic, Azure OpenAI, Gemini, and Mistral AI as reusable LLM providers in AI Workspace."
canonical_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/llm-providers/overview/
md_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/llm-providers/overview.md
tags:
  - cloud
  - ai-workspace
  - llm-providers
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-23
content_type: "overview"
---

# LLM Providers Overview

LLM Providers are integrations with AI service platforms that offer language models. By configuring providers in the AI Workspace, you can:

- **Centralize credential management**: Store API keys and authentication details securely
- **Connect multiple providers**: Integrate with leading LLM services
- **Monitor provider status**: Track availability and health of connected services
- **Simplify configuration**: Use providers across multiple proxies without duplicating credentials

## Supported Providers

API Platform AI Workspace supports the following LLM providers:

| Provider | Description | Learn More |
|----------|-------------|-----------|
| ![OpenAI](https://raw.githubusercontent.com/nomadxd/openapi-connectors/main/openapi/openai/icon.png){: style="width:32px; vertical-align:middle"} **OpenAI** | Access GPT-4, GPT-3.5, and other OpenAI models | [Documentation](https://developers.openai.com/api/docs) |
| ![Anthropic](https://raw.githubusercontent.com/nomadxd/openapi-connectors/main/openapi/anthropic.claude/icon.png){: style="width:32px; vertical-align:middle"} **Anthropic** | Integrate Claude models for advanced AI capabilities | [Documentation](https://docs.anthropic.com/) |
| ![Azure OpenAI](https://raw.githubusercontent.com/nomadxd/openapi-connectors/main/openapi/azure.openai/icon.png){: style="width:32px; vertical-align:middle"} **Azure OpenAI** | Use OpenAI models hosted on Microsoft Azure | [Documentation](https://azure.microsoft.com/products/ai-services/openai-service) |
| ![Azure AI Foundry](https://raw.githubusercontent.com/nomadxd/openapi-connectors/main/openapi/azure.openai/icon.png){: style="width:32px; vertical-align:middle"} **Azure AI Foundry** | Access models through Azure AI Foundry platform | [Documentation](https://azure.microsoft.com/products/ai-studio) |
| ![Gemini](https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg){: style="width:32px; vertical-align:middle"} **Gemini** | Integrate Google's Gemini language models | [Documentation](https://ai.google.dev/gemini-api) |
| ![Mistral AI](https://raw.githubusercontent.com/nomadxd/openapi-connectors/main/openapi/mistral/icon.png){: style="width:32px; vertical-align:middle"} **Mistral AI** | Access Mistral's open and commercial models | [Documentation](https://mistral.ai/) |
| **AWS Bedrock** | Connect to Amazon Bedrock's managed AI service | [Documentation](https://aws.amazon.com/bedrock/) |

## Connecting a Custom Provider

If the LLM service you use isn't in the list above, an organization admin can define a reusable **LLM Provider Template** under **Settings > LLM Provider Templates**. A template captures the endpoint and authentication shape for a custom provider, and it then appears in the provider type selector alongside the built-in providers whenever you add a new provider. Built-in templates are read-only — you can't create new versions from them — but you can enable or disable any template to control whether it's offered when adding a provider.

[//]: # (## Quick Start)

[//]: # ()
[//]: # (To start using LLM Providers:)

[//]: # ()
[//]: # (1. Navigate to AI Workspace in your API Platform dashboard)

[//]: # (2. Select "LLM Providers" from the menu)

[//]: # (3. Click "+ Add New Provider" and choose your provider type)

[//]: # (4. Enter your credentials and configure settings)

[//]: # (5. Save and test the connection)

**Next:** [Configure LLM Provider](configure-provider.md) - Step-by-step guide to set up your first provider