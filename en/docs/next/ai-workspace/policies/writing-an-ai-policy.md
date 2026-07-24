---
title: "Write an AI policy for the AI Gateway"
description: "Build a custom AI policy using the gateway SDK, including support for buffered and streaming (SSE) LLM request and response bodies."
canonical_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/policies/writing-an-ai-policy/
md_url: https://wso2.com/api-platform/docs/cloud/ai-workspace/policies/writing-an-ai-policy.md
tags:
  - cloud
  - ai-workspace
  - custom-policy
  - sdk
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-24
content_type: "how-to"
---

# Writing an AI Policy for the AI Gateway

AI policies allow you to inspect, control, and modify traffic going to and from Large Language Models (LLMs), such as OpenAI, Anthropic, or other providers.

AI policies use the same `Policy` interface as standard gateway policies. For full API details, see the [SDK Documentation](https://pkg.go.dev/github.com/wso2/api-platform/sdk/core/policy/v1alpha2).

The key difference is how you handle LLM request and response bodies, especially:

- JSON responses
- Streaming responses (SSE)

## How It Works

Every request and response that flows through the gateway passes through a **policy chain**. Each policy declares which phases it participates in, and the kernel calls the appropriate hook for each phase:

```text
Incoming Request
       │
       ▼
  Request Headers  ──► OnRequestHeaders()
       │
       ▼
  Request Body     ──► OnRequestBody()  (or OnRequestBodyChunk() for streaming)
       │
       ▼
   Upstream LLM
       │
       ▼
  Response Headers ──► OnResponseHeaders()
       │
       ▼
  Response Body    ──► OnResponseBody() (or OnResponseBodyChunk() for streaming)
       │
       ▼
  Downstream Client
```

!!! note
    A **policy chain** is an ordered sequence of policies that the gateway runs on every request and response for a given LLM Provider or App LLM Proxy. Policies execute in the order they are listed in the runtime configuration — each policy sees the modifications made by the ones before it.

## Key Idea

LLM responses come in two formats:

| Mode | Format |
|------|--------|
| Non-streaming | Single JSON object |
| Streaming | SSE events (`data: {...}`) |

Your policy must be implemented to handle **both formats**.

## Which Interfaces to Implement

Choose based on what your policy needs to do:

| Goal | Interface | Mode Setting |
|------|-----------|-------------|
| Inspect prompt / model | `RequestPolicy` | `RequestBodyMode: BodyModeBuffer` |
| Inspect headers (auth, routing) | `RequestHeaderPolicy` | `RequestHeaderMode: HeaderModeProcess` |
| Inspect or modify buffered (in-memory) response | `ResponsePolicy` | `ResponseBodyMode: BodyModeBuffer` |
| Inspect or modify streaming response | `StreamingResponsePolicy` (embeds `ResponsePolicy`) | `ResponseBodyMode: BodyModeStream` |

## How to Write an AI Policy

### Step 1: Create the Policy

Each policy lives in its own Go module. Create a "policies" directory inside your gateway:

```text
/policies/my-ai-policy/
 ├── go.mod
 ├── my_ai_policy.go
 └── policy-definition.yaml
```

### Step 2: Implement the Mode

`Mode()` declares which phases this policy participates in and how bodies are handled. The kernel reads this once at startup — there is no per-request overhead.

```go
package myaipolicy

import (
    "context"

    policy "github.com/wso2/api-platform/sdk/core/policy/v1alpha2"
)

type MyAIPolicy struct{}

func (p *MyAIPolicy) Mode() policy.ProcessingMode {
    return policy.ProcessingMode{
        RequestBodyMode:  policy.BodyModeBuffer,
        ResponseBodyMode: policy.BodyModeStream,
    }
}
```

!!! tip
    If your policy does not need to inspect a phase, explicitly set it to `HeaderModeSkip` or `BodyModeSkip`.

### Step 3: Implement Request Inspection

`OnRequestBody` is called once the request body is fully buffered. Use it to inspect the model name, messages, or parameters before the request reaches the LLM provider.

```go
func (p *MyAIPolicy) OnRequestBody(
    ctx context.Context,
    reqCtx *policy.RequestContext,
    params map[string]interface{},
) policy.RequestAction {
    // Inspect model + messages
    return nil
}
```

### Step 4: Implement Response Handling

For most AI policies, implement both:

- **`ResponsePolicy`** - Handles buffered responses where the entire response is available at once. This could be a non-streaming JSON response or concatenated SSE events.
- **`StreamingResponsePolicy`** - Handles streaming responses, which could be JSON or SSE events.

!!! tip
    The gateway automatically chooses which handler to call. `OnResponseBodyChunk` is invoked only if the entire policy chain is streaming-compatible. If any policy in the chain does not support streaming, `OnResponseBody` is used as a fallback — implement both even if streaming is your primary target.

```go
// Streaming Response Handling
func (p *MyAIPolicy) OnResponseBodyChunk(
    ctx context.Context,
    respCtx *policy.ResponseStreamContext,
    chunk *policy.StreamBody,
    params map[string]interface{},
) policy.StreamingResponseAction {
    // Accumulate + process
    return policy.ForwardResponseChunk{}
}

// Gating response chunks before processing response
func (p *MyAIPolicy) NeedsMoreResponseData(_ []byte) bool {
    return false
}

// Buffered Fallback
func (p *MyAIPolicy) OnResponseBody(
    ctx context.Context,
    respCtx *policy.ResponseContext,
    params map[string]interface{},
) policy.ResponseAction {
    // Same logic as streaming, applied to the full body
    return nil
}
```

#### Gate-then-Stream Pattern

A common pattern for AI guardrails is to accumulate chunks until you have a complete SSE event to inspect, then switch to pass-through:

```go
// Buffer until we can parse a complete SSE event, then stream freely
func (p *MyAIPolicy) NeedsMoreResponseData(accumulated []byte) bool {
    return !bytes.Contains(accumulated, []byte("\n\n"))
}
```

### Step 5: Factory Function

Initialize your policy and validate parameters:

```go
func GetPolicy(
    metadata policy.PolicyMetadata,
    params map[string]interface{},
) (policy.Policy, error) {

    threshold, ok := params["blockThreshold"].(float64)
    if !ok {
        return nil, fmt.Errorf("invalid blockThreshold")
    }

    return &MyAIPolicy{blockThreshold: threshold}, nil
}
```

### Step 6: Define Parameters

Create a `policy-definition.yaml` in your policy directory:

```yaml
name: my-ai-policy
displayName: my ai policy
version: v1.0.0

parameters:
  type: object
  properties:
    blockThreshold:
      type: number
      default: 0.8
```

### Step 7: Share Data Between Phases

Use the `Metadata` map to pass data between request and response phases — for example, the model name read from the request, used later to apply model-specific logic in the response phase:

```go
// In request phase
reqCtx.Metadata["model"] = model

// In response phase
model := respCtx.Metadata["model"]
```

### Step 8: Register and Build

Add your policy to the gateway folder's `build.yaml` under `policies:` using `filePath` for local development:

```yaml
policies:
  - name: my-ai-policy
    filePath: ./policies/my-ai-policy
```

For published policies (production), use the module reference instead:

```yaml
policies:
  - name: my-ai-policy
    gomodule: github.com/abc/policy-repo/policies/my-ai-policy@v1
```

## Best Practices

- **Always handle both streaming and non-streaming** - The gateway may fall back to buffered mode if any policy in the chain does not support streaming.
- **Use Metadata to share state** - Pass data between request and response phases using the `Metadata` map.
- **Implement streaming + fallback for compatibility** - Ensure your policy works correctly regardless of whether the chain runs in streaming or buffered mode.
- **Parse SSE incrementally** - When gating on streaming responses, buffer only until you have a complete SSE event (`\n\n`-terminated) rather than the entire response, to keep latency low.

## What's Next?

- [Building the Gateway with AI Policies](build-gateway-with-ai-policies.md): Build a gateway image that includes your custom AI policy
- [Apply AI Policies to Proxies](apply-ai-policies-to-proxies.md): Sync your custom AI policy to the organization and apply it to LLM Providers and App LLM Proxies
- [Writing a Custom Policy for the Self-Hosted Gateway](../../../cloud/api-platform-gateway/writing-a-custom-policy.md): Learn about the general-purpose policy SDK that the AI Gateway's policy engine builds on
