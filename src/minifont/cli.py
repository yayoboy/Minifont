"""Command-line interface for Minifont."""

import sys
import click
from pathlib import Path
from typing import Optional

from .font_loader import FontLoader, FontLoaderError
from .charset import Charset, CharsetError
from .rasterizer import FontRasterizer, RasterizerError
from .exporters import (
    CHeaderExporter,
    XBMExporter,
    BDFExporter,
    PythonExporter,
    ExporterError
)


EXPORT_FORMATS = {
    'c-header': ('.h', CHeaderExporter),
    'xbm': ('.xbm', XBMExporter),
    'bdf': ('.bdf', BDFExporter),
    'python': ('.py', PythonExporter),
}


def print_success(message: str) -> None:
    """Print success message in green."""
    click.secho(f"✓ {message}", fg='green')


def print_error(message: str) -> None:
    """Print error message in red."""
    click.secho(f"✗ {message}", fg='red', err=True)


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    click.secho(f"⚠ {message}", fg='yellow')


def print_info(message: str) -> None:
    """Print info message in cyan."""
    click.secho(f"ℹ {message}", fg='cyan')


@click.command()
@click.option(
    '--font', '-f',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to font file (TTF, OTF, WOFF, WOFF2)'
)
@click.option(
    '--size', '-s',
    type=int,
    default=16,
    help='Font size in pixels (default: 16)'
)
@click.option(
    '--charset', '-c',
    type=str,
    help='Character set: preset name (ascii, extended) or range (32-126, 32-90,160-255)'
)
@click.option(
    '--format', '-F',
    'output_format',
    type=click.Choice(list(EXPORT_FORMATS.keys()), case_sensitive=False),
    help='Export format'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output file path'
)
@click.option(
    '--preview', '-p',
    is_flag=True,
    help='Show text preview of generated bitmaps'
)
@click.option(
    '--list-presets',
    is_flag=True,
    help='List available character set presets'
)
@click.version_option(version='0.1.0', prog_name='minifont')
def main(
    font: Optional[Path],
    size: int,
    charset: Optional[str],
    output_format: Optional[str],
    output: Optional[Path],
    preview: bool,
    list_presets: bool
):
    """Minifont - Convert fonts to 1-bit bitmaps for Arduino and embedded projects.

    Run without arguments for interactive mode.
    """
    # Handle list-presets flag
    if list_presets:
        print_info("Available character set presets:")
        for preset in Charset.get_all_presets():
            start, end = Charset.PRESETS[preset]
            print(f"  • {preset}: characters {start}-{end}")
        return

    # Interactive mode if no arguments provided
    if not font:
        interactive_mode()
        return

    # Batch mode
    if not charset:
        print_error("--charset is required in batch mode")
        sys.exit(1)

    if not output_format:
        print_error("--format is required in batch mode")
        sys.exit(1)

    try:
        process_font(font, size, charset, output_format, output, preview)
    except (FontLoaderError, CharsetError, RasterizerError, ExporterError) as e:
        print_error(str(e))
        sys.exit(1)


def interactive_mode():
    """Run in interactive mode with prompts."""
    click.echo()
    click.secho("╔═══════════════════════════════════════╗", fg='cyan')
    click.secho("║         Minifont v0.1.0              ║", fg='cyan', bold=True)
    click.secho("║  Font to Bitmap Converter for Arduino║", fg='cyan')
    click.secho("╚═══════════════════════════════════════╝", fg='cyan')
    click.echo()

    # Step 1: Select font file
    font_path = click.prompt(
        click.style("Font file path", fg='yellow'),
        type=click.Path(exists=True, dir_okay=False, path_type=Path)
    )

    # Step 2: Select font size
    font_size = click.prompt(
        click.style("Font size in pixels", fg='yellow'),
        type=int,
        default=16
    )

    # Step 3: Select character set
    click.echo()
    print_info("Character set presets:")
    for preset in Charset.get_all_presets():
        print(f"  • {preset}")
    click.echo("  • custom (define your own range)")

    charset_input = click.prompt(
        click.style("Character set (preset name or range like '32-126')", fg='yellow'),
        type=str,
        default='ascii'
    )

    # Step 4: Select output format
    click.echo()
    print_info("Available export formats:")
    for fmt, (ext, _) in EXPORT_FORMATS.items():
        print(f"  • {fmt} ({ext})")

    output_format = click.prompt(
        click.style("Export format", fg='yellow'),
        type=click.Choice(list(EXPORT_FORMATS.keys()), case_sensitive=False),
        default='c-header'
    )

    # Step 5: Output file path
    default_ext = EXPORT_FORMATS[output_format][0]
    default_output = f"font_output{default_ext}"

    output_path = click.prompt(
        click.style("Output file path", fg='yellow'),
        type=click.Path(path_type=Path),
        default=default_output
    )

    # Step 6: Preview option
    preview = click.confirm(
        click.style("Show preview of generated bitmaps?", fg='yellow'),
        default=False
    )

    click.echo()
    click.secho("Processing...", fg='cyan', bold=True)
    click.echo()

    try:
        process_font(font_path, font_size, charset_input, output_format, output_path, preview)
    except (FontLoaderError, CharsetError, RasterizerError, ExporterError) as e:
        print_error(str(e))
        sys.exit(1)


def process_font(
    font_path: Path,
    size: int,
    charset_input: str,
    output_format: str,
    output_path: Optional[Path],
    preview: bool
):
    """Process font conversion with given parameters."""

    # Load font
    print_info(f"Loading font: {font_path.name}")
    loader = FontLoader(str(font_path))
    loader.validate()
    font_name = loader.get_font_name()
    print_success(f"Font loaded: {font_name}")

    # Parse character set
    print_info(f"Parsing character set: {charset_input}")

    # Check if it's a preset or custom range
    if charset_input.lower() in Charset.get_all_presets():
        char_codes = Charset.get_preset(charset_input.lower())
    else:
        char_codes = Charset.parse_range(charset_input)

    # Filter to available characters
    available = loader.get_available_characters()
    available_chars = Charset.filter_available(char_codes, available)
    missing_chars = Charset.get_missing(char_codes, available)

    print_success(f"Character set: {len(available_chars)} characters")

    if missing_chars:
        print_warning(f"{len(missing_chars)} characters not available in font")

    # Rasterize glyphs
    print_info(f"Rasterizing glyphs at {size}px...")
    rasterizer = FontRasterizer(str(font_path), size)
    glyphs = rasterizer.rasterize_charset(available_chars)

    if not glyphs:
        raise RasterizerError("No glyphs could be rasterized")

    print_success(f"Rasterized {len(glyphs)} glyphs")

    # Show preview if requested
    if preview:
        click.echo()
        print_info("Bitmap preview (first 3 characters):")
        click.echo()
        for glyph in glyphs[:3]:
            preview_text = rasterizer.preview_glyph(glyph)
            click.echo(preview_text)
            click.echo()

    # Export
    if output_path is None:
        ext = EXPORT_FORMATS[output_format][0]
        output_path = Path(f"{font_name.lower()}{size}{ext}")

    print_info(f"Exporting to {output_format} format: {output_path}")

    exporter_class = EXPORT_FORMATS[output_format][1]
    exporter = exporter_class(font_name, size) if output_format == 'bdf' else exporter_class(font_name)
    exporter.export(glyphs, str(output_path))

    print_success(f"Export complete: {output_path}")

    # Show file info
    file_size = output_path.stat().st_size
    print_info(f"File size: {file_size} bytes")

    click.echo()
    click.secho("✓ Done!", fg='green', bold=True)


if __name__ == '__main__':
    main()
