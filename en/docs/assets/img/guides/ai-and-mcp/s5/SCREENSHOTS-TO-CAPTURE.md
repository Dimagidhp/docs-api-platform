# Screenshots to capture for observe-ai-gateway-traffic.md

Five images are referenced by `en/docs/guides/ai-and-mcp/observe-ai-gateway-traffic.md`.
Drop each PNG into this folder under the exact filename below. Until then the page
renders with five broken image icons.

| # | Filename | Step | What to capture |
|---|---|---|---|
| 1 | `insights-overview.png` | Step 3 | The Insights page overview panel (Total Requests, Avg Latency, Success Rate) with the Request Trend chart below it, showing real traffic. |
| 2 | `insights-token-usage.png` | Step 3 | The token usage view, with prompt / completion / total tokens broken down by model and provider. |
| 3 | `runtime-logs-gateway-code.png` | Step 4 | Observability > Logs with one gateway log entry expanded, so `gatewayCode`, `CorrelationID`, and `Duration` are all legible. Capture an `AUTH_FAILURE` entry if possible, since the step walks the reader to that one. |
| 4 | `grafana-ai-gateway-overview.png` | Step 5 | The AI Gateway Overview dashboard in Grafana with a minute of traffic on it — the four stat tiles plus the request-rate and policy-rejection panels. `./load.sh` in the sample produces suitable data. |
| 5 | `jaeger-trace-detail.png` | Step 6 | One Jaeger trace open on the timeline view, showing router and policy-engine spans with visibly different durations. |

## Conventions (from the API Platform doc style guide)

- PNG, no transparent background.
- Crop tightly to the relevant UI; keep the same OS and window chrome across all five.
- No personally identifying information. Cover anything sensitive with a solid 100%-opacity
  block, never a blur or mosaic — both are reversible. Flatten layers on export.
- Alt text is already written into the page; don't change the filenames without updating it.

Delete this file once all five images are in place.
