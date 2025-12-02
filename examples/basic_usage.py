"""Basic usage examples for Minifont library."""

from minifont import FontLoader, FontRasterizer, CHeaderExporter
from minifont.charset import Charset


def example_basic_conversion():
    """Example: Convert a font to C header format."""
    print("Example 1: Basic font conversion to C header\n")

    # Load the font
    font_path = "path/to/your/font.ttf"
    loader = FontLoader(font_path)
    loader.validate()

    print(f"Font loaded: {loader.get_font_name()}")

    # Get ASCII character set
    char_codes = Charset.get_preset('ascii')
    print(f"Character set: {len(char_codes)} characters")

    # Filter to available characters
    available = loader.get_available_characters()
    char_codes = Charset.filter_available(char_codes, available)

    # Rasterize glyphs
    rasterizer = FontRasterizer(font_path, size=16)
    glyphs = rasterizer.rasterize_charset(char_codes)

    print(f"Rasterized: {len(glyphs)} glyphs")

    # Export to C header
    exporter = CHeaderExporter("MyFont")
    exporter.export(glyphs, "output/myfont16.h")

    print("✓ Export complete: output/myfont16.h\n")


def example_custom_charset():
    """Example: Use custom character range."""
    print("Example 2: Custom character range\n")

    font_path = "path/to/your/font.ttf"
    loader = FontLoader(font_path)

    # Define custom range: digits, uppercase letters, and some symbols
    char_codes = Charset.parse_range("48-57,65-90,33,63")  # 0-9, A-Z, !, ?

    print(f"Custom charset: {Charset.format_charset_info(char_codes)}")

    # Continue with rasterization and export...
    print()


def example_preview_glyphs():
    """Example: Preview generated bitmaps."""
    print("Example 3: Preview glyph bitmaps\n")

    font_path = "path/to/your/font.ttf"
    rasterizer = FontRasterizer(font_path, size=12)

    # Rasterize letter 'A'
    glyph = rasterizer.rasterize_glyph(65)

    if glyph:
        # Display text preview
        preview = rasterizer.preview_glyph(glyph)
        print(preview)

    print()


def example_multiple_formats():
    """Example: Export to multiple formats."""
    print("Example 4: Export to multiple formats\n")

    from minifont.exporters import XBMExporter, BDFExporter

    font_path = "path/to/your/font.ttf"
    loader = FontLoader(font_path)

    char_codes = Charset.get_preset('ascii')
    available = loader.get_available_characters()
    char_codes = Charset.filter_available(char_codes, available)

    rasterizer = FontRasterizer(font_path, size=16)
    glyphs = rasterizer.rasterize_charset(char_codes)

    # Export to C header
    c_exporter = CHeaderExporter("MyFont")
    c_exporter.export(glyphs, "output/myfont.h")
    print("✓ C header: output/myfont.h")

    # Export to XBM
    xbm_exporter = XBMExporter("MyFont")
    xbm_exporter.export(glyphs, "output/myfont.xbm")
    print("✓ XBM: output/myfont.xbm")

    # Export to BDF
    bdf_exporter = BDFExporter("MyFont", font_size=16)
    bdf_exporter.export(glyphs, "output/myfont.bdf")
    print("✓ BDF: output/myfont.bdf")

    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Minifont Usage Examples")
    print("=" * 60)
    print()

    print("NOTE: Update font_path variables with actual font file paths\n")

    # Uncomment to run examples:
    # example_basic_conversion()
    # example_custom_charset()
    # example_preview_glyphs()
    # example_multiple_formats()

    print("See source code for implementation details")
