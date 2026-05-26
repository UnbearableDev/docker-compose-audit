"""Tests for DCS-037: Image uses :latest tag or no tag — fix_yaml_snippet correctness."""
import asyncio
import pytest

from compose_audit import checks as registry
from compose_audit.parser import resolve_compose_input


def _findings_for_yaml(yaml_text: str):
    doc = asyncio.get_event_loop().run_until_complete(
        resolve_compose_input(yaml_text, None)
    )
    return [f for f in registry.run_all(doc) if f.id == 'DCS-037']


def _snippet(image_line: str) -> str:
    yaml_text = f"version: '3.8'\nservices:\n  svc:\n    {image_line}\n"
    findings = _findings_for_yaml(yaml_text)
    assert findings, f"DCS-037 did not fire for: {image_line}"
    return findings[0].fix_yaml_snippet


class TestDCS037SnippetTagStripping:
    def test_latest_tag_stripped(self):
        """image: nginx:latest -> snippet should NOT include ':latest'"""
        snippet = _snippet("image: nginx:latest")
        assert snippet == "    image: nginx:<specific-version>", repr(snippet)

    def test_no_tag_image(self):
        """image: nginx (no tag) -> snippet should be image: nginx:<specific-version>"""
        snippet = _snippet("image: nginx")
        assert snippet == "    image: nginx:<specific-version>", repr(snippet)

    def test_registry_path_latest(self):
        """gcr.io/distroless/python:latest -> registry path preserved, tag stripped"""
        snippet = _snippet("image: gcr.io/distroless/python:latest")
        assert snippet == "    image: gcr.io/distroless/python:<specific-version>", repr(snippet)

    def test_registry_with_port_latest(self):
        """localhost:5000/foo:latest -> port preserved, only trailing tag stripped"""
        snippet = _snippet("image: localhost:5000/foo:latest")
        assert snippet == "    image: localhost:5000/foo:<specific-version>", repr(snippet)

    def test_pinned_image_no_finding(self):
        """image: nginx:1.25.3 -> DCS-037 must NOT fire"""
        yaml_text = "version: '3.8'\nservices:\n  svc:\n    image: nginx:1.25.3\n"
        findings = _findings_for_yaml(yaml_text)
        assert not findings, f"Unexpected DCS-037 for pinned image: {findings}"
