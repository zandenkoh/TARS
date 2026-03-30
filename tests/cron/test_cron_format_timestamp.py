"""Tests for CronTool._format_timestamp() function."""

import pytest
from datetime import datetime, timezone
from TARS.agent.tools.cron import CronTool

# timestamp for 2024-01-01 12:00:00 UTC = 1704110400000
TEST_MS = 1704110400000

def test_format_timestamp_utc():
    # UTC
    result = CronTool._format_timestamp(TEST_MS, "UTC")
    assert result == "2024-01-01 12:00:00 UTC"

def test_format_timestamp_valid_timezone():
    # America/New_York (EST/EDT)
    # 2024-01-01 is EST (UTC-5)
    result = CronTool._format_timestamp(TEST_MS, "America/New_York")
    assert result == "2024-01-01 07:00:00 EST"

    # Asia/Tokyo (JST, UTC+9)
    result = CronTool._format_timestamp(TEST_MS, "Asia/Tokyo")
    assert result == "2024-01-01 21:00:00 JST"

def test_format_timestamp_invalid_timezone():
    # Should fallback to UTC format
    result = CronTool._format_timestamp(TEST_MS, "Invalid/Timezone")
    assert result == "2024-01-01 12:00:00 UTC"

def test_format_timestamp_none_timezone():
    # Exception on None timezone (TypeError usually), caught by except block
    result = CronTool._format_timestamp(TEST_MS, None)  # type: ignore
    assert result == "2024-01-01 12:00:00 UTC"

def test_format_timestamp_different_time():
    # test a different time just to be sure
    # 2026-03-17 02:00:00 CST (from existing tests) -> 1773684000000 ms
    result = CronTool._format_timestamp(1773684000000, "Asia/Shanghai")
    assert result == "2026-03-17 02:00:00 CST"

def test_format_timestamp_fractional_ms():
    # 1704110400123 ms -> 123 fraction
    # The current formatting string "%Y-%m-%d %H:%M:%S %Z" does not show ms,
    # but we should ensure the division ms / 1000.0 doesn't break things.
    result = CronTool._format_timestamp(1704110400123, "UTC")
    assert result == "2024-01-01 12:00:00 UTC"
