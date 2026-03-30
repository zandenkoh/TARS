import pytest

from TARS.cli.models import format_token_count

def test_format_token_count_under_1k():
    """Test format_token_count for values under 1000."""
    assert format_token_count(0) == "0"
    assert format_token_count(5) == "5"
    assert format_token_count(999) == "999"

def test_format_token_count_k():
    """Test format_token_count for values in the thousands."""
    assert format_token_count(1000) == "1.0k"
    assert format_token_count(1500) == "1.5k"
    assert format_token_count(999900) == "999.9k"
    assert format_token_count(1550) == "1.6k"

def test_format_token_count_m():
    """Test format_token_count for values in the millions."""
    assert format_token_count(1000000) == "1.0M"
    assert format_token_count(1500000) == "1.5M"
    assert format_token_count(10000000) == "10.0M"

def test_format_token_count_rounding():
    """Test format_token_count rounds correctly."""
    assert format_token_count(1234) == "1.2k"
    assert format_token_count(1250) in ["1.2k", "1.3k"] # usually rounds to even
    assert format_token_count(1999) == "2.0k"
    assert format_token_count(1234567) == "1.2M"
    assert format_token_count(1999999) == "2.0M"
