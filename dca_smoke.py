"""Smoke test: parse bad-compose fixture, run all checks, list MCP tools."""
import asyncio
import json
from pathlib import Path

from compose_audit import checks as registry
from compose_audit.findings import summarize
from compose_audit.parser import resolve_compose_input


async def main():
    yaml_text = Path('tests/fixtures/bad-compose.yml').read_text()
    print(f"Loaded fixture: {len(yaml_text)} bytes\n")

    doc = await resolve_compose_input(yaml_text, None)
    print(f"Parsed: version={doc.version} services={list(doc.services.keys())}\n")

    findings = registry.run_all(doc)
    summary = summarize(findings)
    print("=" * 70)
    print(f"SUMMARY: {summary['total_findings']} findings")
    print(f"  by severity: {summary['by_severity']}")
    print(f"  by category: {summary['by_category']}")
    print(f"  services with findings: {summary['services_with_findings']}")
    print("=" * 70)
    print()

    # Group findings by service for readability
    by_service: dict[str, list] = {}
    for f in findings:
        by_service.setdefault(f.service or '<top-level>', []).append(f)

    for svc, svc_findings in by_service.items():
        print(f"\n--- service: {svc} ---")
        for f in sorted(svc_findings, key=lambda x: (-{'high':3,'medium':2,'low':1,'info':0}[x.severity], x.id)):
            print(f"  [{f.severity.upper():6}] {f.id}: {f.title}")

    # Verify specific expected findings appear
    print("\n" + "=" * 70)
    print("EXPECTED FINDINGS CHECK")
    expected = ['DCS-001', 'DCS-002', 'DCS-003', 'DCS-006', 'DCS-010', 'DCS-013',
                'DCS-014', 'DCS-018', 'DCS-020', 'DCS-026', 'DCS-027', 'DCS-032',
                'DCS-037', 'DCS-043', 'DCS-051']
    seen_ids = {f.id for f in findings}
    for eid in expected:
        ok = '✓' if eid in seen_ids else '✗'
        print(f"  {ok} {eid}")
    print("=" * 70)

    # Now verify MCP server registers all expected tools
    print("\n--- MCP SERVER TOOLS ---")
    from compose_audit.main import get_server
    server = get_server()
    tools = await server.list_tools()
    print(f"Registered: {len(tools)} tools on '{server.name}'")
    for t in tools:
        print(f"  - {t.name}")

    print("\n--- CHECK CATALOG (first 5) ---")
    for entry in registry.catalog()[:5]:
        print(f"  {entry['id']} [{entry['severity']:6}] ({entry['category']}) — {entry['title']}")
    print(f"  ... ({len(registry.catalog())} total)")


if __name__ == '__main__':
    asyncio.run(main())
