---
title: "Webhook event catalog"
description: "Every webhook event the API Portal & MCP Hub publishes, with its payload fields, the delivery envelope, headers, signature verification, and field encryption."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/references/webhook-event-catalog/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/references/webhook-event-catalog.md
tags:
  - cloud
  - api-portal
  - webhooks
  - reference
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-31
content_type: "reference"
---

# Webhook Event Catalog

The portal publishes twelve event types. This page gives the delivery envelope, the headers, how to verify and decrypt a delivery, and the exact `data` fields for every event.

To register an endpoint and choose which events it receives, see [Webhook Integration](../admin-settings/webhook-integration.md).

## The Delivery Envelope

Every delivery is a `POST` with the same outer shape, whatever the event:

```json
{
  "event_id": "6f1b0e42-2c9a-4f7e-9a1d-8f2b5c3d7e10",
  "event_type": "apikey.generated",
  "occurred_at": "2026-07-31T09:12:04.512Z",
  "org": { "ref_id": "acme-org" },
  "encrypted_fields": ["key"],
  "data": {
    "key_id": "…",
    "key": { "iv": "…", "tag": "…", "ciphertext": "…" }
  }
}
```

| Field | Meaning |
|---|---|
| `event_id` | Unique id for the event. Stable across every subscriber that receives it — use it to deduplicate |
| `event_type` | One of the types in the catalog below |
| `occurred_at` | When the event was recorded, not when it was delivered |
| `org.ref_id` | The organization's control-plane reference id, falling back to its internal UUID when unset |
| `encrypted_fields` | Names of the keys in `data` that hold an encrypted envelope rather than a plain value. Empty for most events |
| `data` | The event's own fields, from the catalog below, plus one entry per encrypted field |

## Headers

| Header | Always sent | Value |
|---|---|---|
| `Content-Type` | Yes | `application/json` |
| `X-Api-Portal-Event` | Yes | The event type, so you can route without parsing the body |
| `X-Api-Portal-Event-Id` | Yes | Same value as `event_id` |
| `X-Api-Portal-Delivery-Id` | Yes | Unique per delivery attempt, per subscriber. Differs between two subscribers receiving the same event |
| `X-Api-Portal-Signature` | When the subscriber has a secret | See below |

## Verify the Signature

The signature header looks like this:

```text
X-Api-Portal-Signature: t=1785490324,v1=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
```

To verify:

1. Split the header on `,` and read `t` (Unix seconds) and `v1` (hex digest).
2. Compute `HMAC-SHA256(secret, "<t>.<raw_body>")` over the **raw** request body, before any JSON parsing or re-serialization.
3. Compare against `v1` with a constant-time comparison.
4. Reject the delivery if `|now - t|` exceeds your tolerance. The portal's own verifier defaults to 300 seconds.

## Decrypt Sensitive Fields

Four events carry a credential. It never appears in plaintext in the body, and it is never stored in the portal's event record — it is encrypted per subscriber at publish time.

Each encrypted field in `data` is an object:

```json
{ "iv": "<base64>", "tag": "<base64>", "ciphertext": "<base64>" }
```

The cipher is **AES-256-GCM**, under a key **derived from that subscriber's shared secret** — the same secret used for the signature. There is no separate key pair and no public key to configure. To decrypt: derive the field key from your secret, then AES-256-GCM decrypt `ciphertext` with that key, `iv`, and `tag`.

!!! important
    A subscriber with no secret still receives these events, just without the encrypted fields — `encrypted_fields` comes back empty and the credential is absent entirely. It is never downgraded to plaintext. Set a secret on any subscriber that needs to read credentials.

## Delivery Semantics

- **A 2xx response means delivered.** Any other status, a connection error, or a timeout marks the delivery failed.
- **There is no retry.** A failure is terminal — the portal records it and moves on. Your endpoint has to be reliable, and it has to answer within the subscriber's timeout (5000 ms unless you change it).
- **Deliveries are per subscriber.** One event matching three subscribers produces three deliveries, each with its own delivery id, signature, and encrypted fields.
- **Order isn't guaranteed.** Events are dispatched from a polled queue, so use `occurred_at` rather than arrival order when sequence matters.
- **A delivery left in flight by a stopped worker** is marked failed after five minutes rather than hanging indefinitely.

Delivery history is readable through the Management API — see [Webhook Events](../rest-api/webhook-events.md).

## Subscription Events

All five share the same base `data`:

| Field | Notes |
|---|---|
| `subscription_id` | The subscription's UUID |
| `subscriber_id` | The developer who owns the subscription |
| `status` | `ACTIVE` or `INACTIVE` |
| `subscription_plan.ref_id` | The plan's control-plane reference id, or `null` |
| `subscription_plan.name` | The plan's display name, or `null` |
| `api.name`, `api.version`, `api.type` | The artifact subscribed to. `api.type` is `Mcp` for an MCP server |
| `api.ref_id` | The artifact's gateway reference, or `""` |

```json
{
  "subscription_id": "b2c3…",
  "subscriber_id": "user-42",
  "status": "ACTIVE",
  "subscription_plan": { "ref_id": "gold-ref", "name": "Gold" },
  "api": { "name": "Catalog API", "version": "1.0.0", "ref_id": "catalog-ref", "type": "RestApi" }
}
```

| Event | Fired when | Extra fields | Encrypted field |
|---|---|---|---|
| `subscription.created` | A developer subscribes to an API or MCP server | — | `token` |
| `subscription.updated` | The status changes — suspend or resume | — | — |
| `subscription.plan_changed` | The plan changes in place | `previous_plan.ref_id`, `previous_plan.name` | — |
| `subscription.token_regenerated` | The subscription token is regenerated | — | `token` |
| `subscription.deleted` | A developer unsubscribes | — | — |

The `token` field carries the subscription token, which callers send in the `Subscription-Key` header. On `token_regenerated` it is the **new** token; the previous one is already invalid.

## API Key Events

| Field | Present on | Notes |
|---|---|---|
| `key_id` | All | The key's UUID |
| `handle` | All | The key's URL identifier |
| `display_name` | All | The name the developer gave it |
| `expires_at` | `generated`, `regenerated` | ISO 8601, or `null` when the key never expires |
| `api` | All | `{ name, version, ref_id, type }`, as above |
| `subscription` | When the key came from a subscription | Omitted otherwise |
| `application` | When the key is associated with an application | `{ id, display_name, handle }`. Omitted on `generated`/`regenerated` when unassociated |

```json
{
  "key_id": "c3d4…",
  "handle": "my-prod-key",
  "display_name": "my-prod-key",
  "expires_at": "2027-01-31T00:00:00.000Z",
  "api": { "name": "Catalog API", "version": "1.0.0", "ref_id": "catalog-ref", "type": "RestApi" },
  "application": { "id": "a1b2…", "display_name": "MyApp-Production", "handle": "myapp-production" }
}
```

| Event | Fired when | Encrypted field |
|---|---|---|
| `apikey.generated` | A key is generated | `key` |
| `apikey.regenerated` | A key is rotated | `key` |
| `apikey.revoked` | A key is revoked. No `expires_at` or `application` | — |
| `apikey.application_updated` | A key's application association changes | — |

On `apikey.application_updated`, `application` is the new association, or **`null`** when the association was cleared — including when the application it belonged to was deleted. Generating a key with an application set fires `apikey.generated` **and** an `apikey.application_updated`.

## Application Events

| Field | Notes |
|---|---|
| `application_id` | The application's UUID |
| `display_name` | Its name |
| `handle` | Its URL identifier |
| `description` | Present on `created` and `updated` |
| `type` | Always the literal `"web"` on `created` and `updated`. The portal has no application-type concept, so don't branch on it |

```json
{
  "application_id": "a1b2…",
  "display_name": "MyApp-Production",
  "handle": "myapp-production",
  "description": "Production client for the storefront",
  "type": "web"
}
```

| Event | Fired when | Fields |
|---|---|---|
| `application.created` | A developer creates an application | All of the above |
| `application.updated` | Its name or description changes | All of the above |
| `application.deleted` | An application is deleted | `application_id`, `display_name`, `handle` |

Deleting an application also fires one `apikey.application_updated` per key that was associated with it, each with `application: null`. The keys themselves stay valid — see [Manage Applications](../manage-applications.md).

## Related

- [Webhook Integration](../admin-settings/webhook-integration.md): register a subscriber and pick its events
- [Webhook Subscribers](../rest-api/webhook-subscribers.md): manage subscribers through the Management API
- [Webhook Events](../rest-api/webhook-events.md): read delivery history through the Management API
- [Manage API Keys](../manage-api-keys.md): the lifecycle behind the `apikey.*` events
- [Manage Subscriptions](../manage-subscriptions.md): the lifecycle behind the `subscription.*` events
