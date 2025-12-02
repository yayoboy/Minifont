"""Tests for charset module."""

import pytest
from minifont.charset import Charset, CharsetError


class TestCharset:
    """Test cases for Charset class."""

    def test_parse_single_range(self):
        """Test parsing a single character range."""
        result = Charset.parse_range("32-126")
        assert len(result) == 95
        assert 32 in result
        assert 126 in result
        assert 31 not in result
        assert 127 not in result

    def test_parse_multiple_ranges(self):
        """Test parsing multiple character ranges."""
        result = Charset.parse_range("32-35,48-50")
        assert result == {32, 33, 34, 35, 48, 49, 50}

    def test_parse_single_character(self):
        """Test parsing single character codes."""
        result = Charset.parse_range("65,66,67")
        assert result == {65, 66, 67}

    def test_parse_mixed(self):
        """Test parsing mixed ranges and single characters."""
        result = Charset.parse_range("32-35,65,70-72")
        assert result == {32, 33, 34, 35, 65, 70, 71, 72}

    def test_parse_invalid_range(self):
        """Test that invalid ranges raise errors."""
        with pytest.raises(CharsetError):
            Charset.parse_range("126-32")  # Start > end

    def test_parse_invalid_format(self):
        """Test that invalid formats raise errors."""
        with pytest.raises(CharsetError):
            Charset.parse_range("abc")

        with pytest.raises(CharsetError):
            Charset.parse_range("32-")

    def test_get_preset_ascii(self):
        """Test getting ASCII preset."""
        result = Charset.get_preset("ascii")
        assert len(result) == 95
        assert 32 in result  # space
        assert 126 in result  # ~

    def test_get_preset_extended(self):
        """Test getting extended ASCII preset."""
        result = Charset.get_preset("extended")
        assert len(result) == 224
        assert 32 in result
        assert 255 in result

    def test_get_preset_unknown(self):
        """Test that unknown preset raises error."""
        with pytest.raises(CharsetError):
            Charset.get_preset("unknown_preset")

    def test_filter_available(self):
        """Test filtering to available characters."""
        requested = {32, 33, 34, 35}
        available = {32, 33, 100, 101}

        result = Charset.filter_available(requested, available)
        assert result == {32, 33}

    def test_get_missing(self):
        """Test getting missing characters."""
        requested = {32, 33, 34, 35}
        available = {32, 33, 100, 101}

        result = Charset.get_missing(requested, available)
        assert result == {34, 35}

    def test_format_charset_info(self):
        """Test formatting charset information."""
        char_codes = {65, 66, 67}  # A, B, C
        info = Charset.format_charset_info(char_codes)

        assert "Total: 3" in info
        assert "65" in info

    def test_format_charset_info_empty(self):
        """Test formatting empty charset."""
        info = Charset.format_charset_info(set())
        assert "No characters" in info

    def test_get_all_presets(self):
        """Test getting all preset names."""
        presets = Charset.get_all_presets()
        assert 'ascii' in presets
        assert 'extended' in presets
        assert len(presets) > 0
