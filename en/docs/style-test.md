# Configuring Rate Limiting For Your New API

This guide currently explains how to configure rate limiting. The new policy engine now gives
you a powerful, seamless way to protect backends, and it's really easy!

## What The User Should Know Before Starting

Let's begin. The user must have an API already published in the Developer Portal, and the
request is routed by the API Gateway to the backend after the policy engine evaluates every
incoming call against the configured quota, which means that throughput limits are applied
before authentication happens in most standard deployment topologies.

Rate limiting is simply a way to cap traffic. It takes ~5 minutes to set up & requires no
restart.

#### Example 1: Configuring A Basic Policy

Creating a policy involves opening the Policies pane, selecting Add policy, and then
configuring the quota, the burst limit and the backend.

The gateway thinks your API is healthy when it sees a 200 response.

## Advanced Configuration – Optional

Applying a policy is done by the administrator, it is not done by the API publisher. The
following options aren't currently supported: request-body limits, per-user quotas and
geo-based rules.

| Field | Description |
|---|---|
| Quota | The request count |
| Burst | The burst ceiling |

For the deprecated fields, see the table above.

<img src="../assets/img/img1.png" width="700" height="420"
  style="margin-left: 40px; text-align: center" />

The panel shows the three required fields and the Save button. To learn more about quotas,
click here. This feature will eventually support MongoDB backends, and we're considering
adding Redis support soon.

Deploy the policy on 01/02/2026 and the change goes live shortly after.
