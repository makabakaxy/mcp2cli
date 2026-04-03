"""Tests for preset versioning support."""

from __future__ import annotations

import unittest

from mcp2cli.preset.version import parse_preset_spec
from mcp2cli.preset.models import PresetEntry, PresetIndex


class TestParsePresetSpec(unittest.TestCase):
    def test_simple_name(self) -> None:
        name, ver = parse_preset_spec("mcp-atlassian")
        self.assertEqual(name, "mcp-atlassian")
        self.assertIsNone(ver)

    def test_name_with_version(self) -> None:
        name, ver = parse_preset_spec("mcp-atlassian@1.2.3")
        self.assertEqual(name, "mcp-atlassian")
        self.assertEqual(ver, "1.2.3")

    def test_name_with_latest(self) -> None:
        name, ver = parse_preset_spec("mcp-atlassian@latest")
        self.assertEqual(name, "mcp-atlassian")
        self.assertIsNone(ver)

    def test_name_with_semver(self) -> None:
        name, ver = parse_preset_spec("playwright@0.5.0-beta.1")
        self.assertEqual(name, "playwright")
        self.assertEqual(ver, "0.5.0-beta.1")

    def test_empty_spec_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_preset_spec("")

    def test_whitespace_spec_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_preset_spec("   ")

    def test_empty_version_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_preset_spec("mcp-atlassian@")

    def test_empty_server_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_preset_spec("@1.2.3")

    def test_whitespace_stripped(self) -> None:
        name, ver = parse_preset_spec("  mcp-atlassian@1.2.3  ")
        self.assertEqual(name, "mcp-atlassian")
        self.assertEqual(ver, "1.2.3")


class TestPresetEntryFromDict(unittest.TestCase):
    def test_v2_format(self) -> None:
        data = {
            "server": "mcp-atlassian",
            "latest": "1.3.0",
            "versions": ["1.3.0", "1.2.3"],
            "description": "JIRA + Confluence",
            "updated_at": "2026-04-03T00:00:00Z",
            "server_version": "1.3.0",
            "tool_count": 68,
        }
        entry = PresetEntry.from_dict(data)
        self.assertEqual(entry.server, "mcp-atlassian")
        self.assertEqual(entry.latest, "1.3.0")
        self.assertEqual(entry.versions, ["1.3.0", "1.2.3"])
        self.assertEqual(entry.server_version, "1.3.0")
        self.assertEqual(entry.tool_count, 68)

    def test_v1_format_compat(self) -> None:
        data = {
            "server": "mcp-atlassian",
            "server_version": "1.2.3",
            "tool_count": 65,
            "description": "JIRA + Confluence",
            "updated_at": "2026-04-01T00:00:00Z",
        }
        entry = PresetEntry.from_dict(data)
        self.assertEqual(entry.latest, "1.2.3")
        self.assertEqual(entry.versions, ["1.2.3"])
        self.assertEqual(entry.server_version, "1.2.3")
        self.assertEqual(entry.tool_count, 65)

    def test_v1_format_no_version(self) -> None:
        data = {
            "server": "custom-server",
            "description": "Custom",
            "updated_at": "2026-04-01T00:00:00Z",
        }
        entry = PresetEntry.from_dict(data)
        self.assertEqual(entry.latest, "")
        self.assertEqual(entry.versions, [])


class TestPresetEntryResolveVersion(unittest.TestCase):
    def setUp(self) -> None:
        self.entry = PresetEntry(
            server="mcp-atlassian",
            latest="1.3.0",
            versions=["1.3.0", "1.2.3", "1.1.0"],
            description="JIRA + Confluence",
            updated_at="2026-04-03T00:00:00Z",
        )

    def test_none_returns_latest(self) -> None:
        self.assertEqual(self.entry.resolve_version(None), "1.3.0")

    def test_existing_version(self) -> None:
        self.assertEqual(self.entry.resolve_version("1.2.3"), "1.2.3")

    def test_latest_version(self) -> None:
        self.assertEqual(self.entry.resolve_version("1.3.0"), "1.3.0")

    def test_nonexistent_version_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.entry.resolve_version("9.9.9")
        self.assertIn("9.9.9", str(ctx.exception))
        self.assertIn("mcp-atlassian", str(ctx.exception))


class TestPresetIndexFromDict(unittest.TestCase):
    def test_v2_index(self) -> None:
        data = {
            "version": 2,
            "updated_at": "2026-04-03T00:00:00Z",
            "presets": [
                {
                    "server": "mcp-atlassian",
                    "latest": "1.3.0",
                    "versions": ["1.3.0", "1.2.3"],
                    "description": "JIRA",
                    "updated_at": "2026-04-03T00:00:00Z",
                },
                {
                    "server": "playwright",
                    "latest": "0.5.0",
                    "versions": ["0.5.0"],
                    "description": "Browser",
                    "updated_at": "2026-03-28T00:00:00Z",
                },
            ],
        }
        index = PresetIndex.from_dict(data)
        self.assertEqual(index.version, 2)
        self.assertEqual(len(index.presets), 2)
        self.assertEqual(index.presets[0].latest, "1.3.0")

    def test_v1_index_compat(self) -> None:
        data = {
            "version": 1,
            "updated_at": "2026-04-01T00:00:00Z",
            "presets": [
                {
                    "server": "mcp-atlassian",
                    "server_version": "1.2.3",
                    "tool_count": 65,
                    "description": "JIRA",
                    "updated_at": "2026-04-01T00:00:00Z",
                },
            ],
        }
        index = PresetIndex.from_dict(data)
        self.assertEqual(index.version, 1)
        entry = index.find("mcp-atlassian")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.latest, "1.2.3")
        self.assertEqual(entry.versions, ["1.2.3"])

    def test_find_returns_none_for_unknown(self) -> None:
        index = PresetIndex(version=2, updated_at="", presets=[])
        self.assertIsNone(index.find("nonexistent"))


if __name__ == "__main__":
    unittest.main()
