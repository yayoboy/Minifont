"""Demo of Minifont's enhanced UI capabilities."""

from minifont import ui, FontDiscovery
from minifont.rasterizer import GlyphBitmap
from rich.panel import Panel
from rich.columns import Columns


def demo_header():
    """Demo: Beautiful header."""
    print("=" * 60)
    print("Demo 1: Header")
    print("=" * 60)
    print()

    ui.print_header()


def demo_messages():
    """Demo: Colored message types."""
    print("\n" + "=" * 60)
    print("Demo 2: Message Types")
    print("=" * 60)
    print()

    ui.show_info("This is an info message")
    ui.show_success("This is a success message")
    ui.show_warning("This is a warning message")
    ui.show_error("This is an error message")


def demo_fonts_table():
    """Demo: Font list as table."""
    print("\n" + "=" * 60)
    print("Demo 3: Fonts Table")
    print("=" * 60)
    print()

    # Find fonts in current directory
    fonts = FontDiscovery.find_fonts_in_directory(".")

    if fonts:
        ui.show_fonts_table(fonts[:10], "Available Fonts")
    else:
        ui.show_info("No fonts found in current directory")
        ui.console.print("[dim]Copy some .ttf files here to see the table![/dim]\n")


def demo_grouped_fonts():
    """Demo: Fonts grouped by family."""
    print("\n" + "=" * 60)
    print("Demo 4: Grouped Fonts")
    print("=" * 60)
    print()

    fonts = FontDiscovery.find_fonts_in_directory(".", recursive=True)

    if len(fonts) > 10:
        families = FontDiscovery.group_fonts_by_family(fonts)
        ui.show_fonts_grouped(fonts, families)
    else:
        ui.console.print("[yellow]Need more fonts to show grouping (found {})  [/yellow]\n".format(len(fonts)))


def demo_glyph_preview():
    """Demo: Glyph bitmap preview."""
    print("\n" + "=" * 60)
    print("Demo 5: Glyph Preview")
    print("=" * 60)
    print()

    # Create sample glyphs
    sample_glyphs = [
        GlyphBitmap(
            char_code=65,  # 'A'
            width=8,
            height=12,
            advance_x=8,
            offset_x=0,
            offset_y=12,
            bitmap=bytes([
                0b11111111, 0b10000001, 0b10000001, 0b11111111,
                0b10000001, 0b10000001, 0b10000001, 0b10000001,
                0b00000000, 0b00000000, 0b00000000, 0b00000000
            ])
        ),
        GlyphBitmap(
            char_code=66,  # 'B'
            width=8,
            height=12,
            advance_x=8,
            offset_x=0,
            offset_y=12,
            bitmap=bytes([
                0b11111110, 0b10000010, 0b10000010, 0b11111110,
                0b10000010, 0b10000010, 0b10000010, 0b11111110,
                0b00000000, 0b00000000, 0b00000000, 0b00000000
            ])
        ),
    ]

    # Show single glyph
    panel = ui.show_glyph_preview(sample_glyphs[0])
    ui.console.print(panel)

    ui.console.print()

    # Show comparison
    ui.show_glyphs_comparison(sample_glyphs, max_glyphs=2)


def demo_conversion_summary():
    """Demo: Conversion summary."""
    print("\n" + "=" * 60)
    print("Demo 6: Conversion Summary")
    print("=" * 60)
    print()

    ui.show_conversion_summary(
        font_name="Roboto",
        char_count=95,
        glyph_count=95,
        output_file="roboto16.h",
        file_size=12580,
        format_type="c-header"
    )


def demo_progress_spinner():
    """Demo: Progress spinner."""
    print("\n" + "=" * 60)
    print("Demo 7: Progress Spinner")
    print("=" * 60)
    print()

    import time

    with ui.show_progress_spinner("Processing fonts...") as progress:
        task = progress.add_task("Processing", total=None)
        time.sleep(2)  # Simulate work
        progress.stop()

    ui.show_success("Processing complete!")


def demo_menus():
    """Demo: Menu panels."""
    print("\n" + "=" * 60)
    print("Demo 8: Menu Panels")
    print("=" * 60)
    print()

    charset_menu = ui.create_menu_panel(
        "Character Set Presets",
        [
            "ascii - Basic ASCII (32-126)",
            "extended - Extended ASCII (32-255)",
            "digits - Numbers 0-9",
            "custom - Define your own range"
        ]
    )

    format_menu = ui.create_menu_panel(
        "Export Formats",
        [
            "c-header - C array (Adafruit GFX)",
            "xbm - X BitMap (U8g2)",
            "bdf - Bitmap Distribution Format",
            "python - Python arrays (MicroPython)"
        ]
    )

    # Show side by side
    columns = Columns([charset_menu, format_menu], equal=True, expand=True)
    ui.console.print(columns)


def demo_code_preview():
    """Demo: Code syntax highlighting."""
    print("\n" + "=" * 60)
    print("Demo 9: Code Preview")
    print("=" * 60)
    print()

    sample_code = """
const uint8_t RobotoBitmaps[] PROGMEM = {
  // 'A' (U+0041)
  0xFF, 0x81, 0x81, 0xFF, 0x81, 0x81, 0x81, 0x81,
  // 'B' (U+0042)
  0xFE, 0x82, 0x82, 0xFE, 0x82, 0x82, 0x82, 0xFE,
};
"""

    ui.show_code_preview(sample_code, language="c", title="Generated C Header")


if __name__ == "__main__":
    ui.console.print("[bold yellow]Minifont UI Demo[/bold yellow]\n")
    ui.console.print("[dim]Showcasing the enhanced terminal UI features[/dim]\n")

    demo_header()
    demo_messages()
    demo_fonts_table()
    demo_grouped_fonts()
    demo_glyph_preview()
    demo_conversion_summary()
    demo_progress_spinner()
    demo_menus()
    demo_code_preview()

    ui.console.print("\n" + "=" * 60)
    ui.console.print("[bold green]✓ Demo Complete![/bold green]")
    ui.console.print("=" * 60)
    ui.console.print("\n[dim]Run 'minifont' to see the full interactive experience![/dim]\n")
