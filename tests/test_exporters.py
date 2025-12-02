"""Tests for exporters module."""

import pytest
from pathlib import Path
import tempfile
from minifont.exporters import (
    CHeaderExporter,
    XBMExporter,
    BDFExporter,
    PythonExporter,
    ExporterError,
    BaseExporter
)
from minifont.rasterizer import GlyphBitmap


@pytest.fixture
def sample_glyphs():
    """Create sample glyphs for testing."""
    return [
        GlyphBitmap(
            char_code=65,  # 'A'
            width=8,
            height=12,
            advance_x=8,
            offset_x=0,
            offset_y=12,
            bitmap=bytes([0xFF, 0x81, 0x81, 0xFF, 0x81, 0x81, 0x81, 0x81, 0x00, 0x00, 0x00, 0x00])
        ),
        GlyphBitmap(
            char_code=66,  # 'B'
            width=8,
            height=12,
            advance_x=8,
            offset_x=0,
            offset_y=12,
            bitmap=bytes([0xFE, 0x82, 0x82, 0xFE, 0x82, 0x82, 0x82, 0xFE, 0x00, 0x00, 0x00, 0x00])
        ),
    ]


class TestBaseExporter:
    """Test cases for BaseExporter."""

    def test_sanitize_name_spaces(self):
        """Test sanitizing names with spaces."""
        exporter = BaseExporter("My Font")
        assert exporter.font_name == "My_Font"

    def test_sanitize_name_special_chars(self):
        """Test sanitizing names with special characters."""
        exporter = BaseExporter("Font-Name@123!")
        assert exporter.font_name == "Font_Name_123_"

    def test_sanitize_name_leading_digit(self):
        """Test sanitizing names starting with digits."""
        exporter = BaseExporter("123Font")
        assert exporter.font_name == "Font_123Font"

    def test_sanitize_name_empty(self):
        """Test sanitizing empty name."""
        exporter = BaseExporter("")
        assert exporter.font_name == "CustomFont"


class TestCHeaderExporter:
    """Test cases for CHeaderExporter."""

    def test_export_creates_file(self, sample_glyphs):
        """Test that export creates a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            output_path = f.name

        try:
            exporter = CHeaderExporter("TestFont")
            exporter.export(sample_glyphs, output_path)

            assert Path(output_path).exists()
            content = Path(output_path).read_text()

            # Check for expected content
            assert "TestFont" in content
            assert "uint8_t" in content
            assert "PROGMEM" in content
            assert "#ifndef" in content
            assert "#define" in content

        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_export_empty_glyphs_raises_error(self):
        """Test that exporting empty glyphs raises error."""
        exporter = CHeaderExporter("TestFont")

        with pytest.raises(ExporterError):
            exporter.export([], "/tmp/test.h")

    def test_export_includes_character_data(self, sample_glyphs):
        """Test that exported file includes character data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            output_path = f.name

        try:
            exporter = CHeaderExporter("TestFont")
            exporter.export(sample_glyphs, output_path)

            content = Path(output_path).read_text()

            # Check for character comments
            assert "'A'" in content or "U+0041" in content
            assert "'B'" in content or "U+0042" in content

        finally:
            Path(output_path).unlink(missing_ok=True)


class TestXBMExporter:
    """Test cases for XBMExporter."""

    def test_export_creates_file(self, sample_glyphs):
        """Test that export creates a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xbm', delete=False) as f:
            output_path = f.name

        try:
            exporter = XBMExporter("TestFont")
            exporter.export(sample_glyphs, output_path)

            assert Path(output_path).exists()
            content = Path(output_path).read_text()

            # Check for expected XBM content
            assert "#define" in content
            assert "width" in content
            assert "height" in content
            assert "static unsigned char" in content

        finally:
            Path(output_path).unlink(missing_ok=True)


class TestBDFExporter:
    """Test cases for BDFExporter."""

    def test_export_creates_file(self, sample_glyphs):
        """Test that export creates a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bdf', delete=False) as f:
            output_path = f.name

        try:
            exporter = BDFExporter("TestFont", font_size=16)
            exporter.export(sample_glyphs, output_path)

            assert Path(output_path).exists()
            content = Path(output_path).read_text()

            # Check for expected BDF content
            assert "STARTFONT" in content
            assert "ENDFONT" in content
            assert "STARTCHAR" in content
            assert "ENDCHAR" in content
            assert "BITMAP" in content

        finally:
            Path(output_path).unlink(missing_ok=True)


class TestPythonExporter:
    """Test cases for PythonExporter."""

    def test_export_creates_file(self, sample_glyphs):
        """Test that export creates a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            output_path = f.name

        try:
            exporter = PythonExporter("TestFont")
            exporter.export(sample_glyphs, output_path)

            assert Path(output_path).exists()
            content = Path(output_path).read_text()

            # Check for expected Python content
            assert "bytes([" in content
            assert "TestFont_bitmaps" in content
            assert "TestFont_glyphs" in content

        finally:
            Path(output_path).unlink(missing_ok=True)
