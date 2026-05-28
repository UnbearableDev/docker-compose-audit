# Docker Compose Security Audit

> MCP server that audits `docker-compose.yml` files for security misconfigurations. Trivy-grade check catalog, designed for AI agents — every finding ships with a severity rating, full remediation text, and a YAML fix snippet you can paste.

**Built by [Unbearable Labs](https://github.com/UnbearableDev). Pay-per-event pricing — you only pay when an audit runs.**

---

## Available on

- [Apify Actor Store](https://apify.com/unbearable_dev/docker-compose-audit) — primary, metered usage (PPE)
- MCPize — *pending submission*
- MCP.so — *pending submission*
- PulseMCP — *pending submission*
- Smithery — *pending submission*
- Glama — *pending submission*

**Newsletter:** [Unbearable TechTips Weekly](https://unbearabletechtips.beehiiv.com) · **All Actors:** [github.com/UnbearableDev](https://github.com/UnbearableDev)

## What it does

Point any MCP-capable client (Claude Desktop, Cursor, n8n, Make, Zapier, custom agents) at this server, hand it the contents of a `docker-compose.yml`, and get back a structured report with:

- **Severity** — high / medium / low / info
- **Service** — which compose service the finding affects
- **Description** — what's wrong and why it matters
- **Remediation** — what to do about it
- **Fix snippet** — YAML you can paste directly into the file

## Tools

| Tool | Purpose |
|------|---------|
| `audit_compose(compose_yaml? \| compose_url?, min_severity='low')` | Run all checks, return full report |
| `check_privilege(...)` | Container privilege & capability issues only |
| `check_network(...)` | Network exposure issues only |
| `check_filesystem(...)` | Volume mount & filesystem issues only |
| `check_secrets(...)` | Secret hygiene issues only |
| `check_resources(...)` | Resource limit issues only |
| `check_image_hygiene(...)` | Image tag / registry / pinning issues only |
| `check_runtime_lifecycle(...)` | Healthcheck / restart / init issues only |
| `check_logging(...)` | Logging driver / rotation issues only |
| `check_compose_hygiene(...)` | Deprecated fields / Compose-spec hygiene only |
| `list_checks(category?)` | Browse the full check catalog |

All audit-running tools accept the same input:
- `compose_yaml` (string) — paste the YAML content directly, **OR**
- `compose_url` (string) — public HTTPS URL to fetch (e.g. GitHub raw URL)

Provide exactly one. `min_severity` defaults to `low` (drops `info` findings); set to `medium` or `high` to filter further.

## Example response (truncated)

```json
{
  "summary": {
    "total_findings": 14,
    "by_severity": {"high": 3, "medium": 6, "low": 5, "info": 0},
    "by_category": {"privilege": 4, "network": 3, "secrets": 2, "...": 5}
  },
  "findings": [
    {
      "id": "DCS-002",
      "category": "privilege",
      "severity": "high",
      "service": "web",
      "title": "Privileged mode enabled",
      "description": "Service 'web' has `privileged: true`...",
      "remediation": "Remove `privileged: true`. If you need specific capabilities...",
      "fix_yaml_snippet": "    # remove `privileged: true`; if needed, use cap_add or devices selectively",
      "references": ["CIS-Docker-5.4", "NIST-800-190"]
    },
    ...
  ]
}
```

## Pricing

| Event | USD |
|-------|-----|
| Any audit / check_* tool call | $0.02 |
| `list_checks` discovery call | $0.005 |

You pay only when a tool is invoked. No subscription, no monthly minimums.

## Check catalog (25 live in v1, growing toward 54)

| Category | Live checks |
|----------|------------|
| **Privilege** | Root user (DCS-001), privileged mode (DCS-002), dangerous capabilities (DCS-003), `cap_add: ALL` (DCS-004), `cap_drop: ALL` missing (DCS-005), `no-new-privileges` missing (DCS-006) |
| **Network** | `network_mode: host` (DCS-010), port bound to 0.0.0.0 (DCS-011), SSH port exposed (DCS-013), DB port exposed (DCS-014) |
| **Filesystem** | `/var/run/docker.sock` mount (DCS-018), host root mount (DCS-019), sensitive host paths (DCS-020) |
| **Secrets** | Hardcoded secret in env (DCS-026), secret-pattern env without Docker secrets (DCS-027) |
| **Resources** | No memory limit (DCS-032), no CPU limit (DCS-033), no PID limit (DCS-034) |
| **Image hygiene** | Unpinned / `:latest` image (DCS-037) |
| **Runtime lifecycle** | No healthcheck (DCS-043), no restart policy (DCS-044) |
| **Logging** | No log driver (DCS-048), no log rotation (DCS-049) |
| **Compose hygiene** | Deprecated `version:` field (DCS-051), `depends_on` without healthcheck condition (DCS-052) |

Use `list_checks` to get the canonical, up-to-date catalog with IDs, severities, and titles.

## Connecting from Claude Desktop

Add to your MCP config:

```json
{
  "mcpServers": {
    "compose-audit": {
      "transport": "streamable-http",
      "url": "https://YOUR-ACTOR-URL.apify.actor/mcp"
    }
  }
}
```

(Replace `YOUR-ACTOR-URL` with the Standby URL shown on the Apify Store page after you start the Actor.)

## Limits

- **YAML size:** 1 MB cap per audit call
- **URL fetch:** 5-second timeout, max 3 redirects, HTTPS only
- **Session timeout:** 5 minutes of inactivity

## What's NOT covered (yet)

Pure static analysis of the compose file only. Out of scope for this version:
- Image vulnerability scanning (use Trivy / Grype for that)
- Live container inspection
- Kubernetes / Helm manifests (different surface)
- Dockerfile-specific lint (use Hadolint)

The next 29 checks on the v1.x → v2 roadmap include build-context security, additional capability checks, secret-pattern detection in build args, and registry trust verification.

## Source / contact

Issues, ideas, or false-positive reports: open an issue on the [GitHub repo](https://github.com/UnbearableDev) or email `unbearabledev@gmail.com`.

get the weekly newsletter(https://unbearabletechtips.beehiiv.com).
