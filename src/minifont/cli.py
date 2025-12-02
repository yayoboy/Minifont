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
from .google_fonts import GoogleFontsDownloader, GoogleFontsError, POPULAR_GOOGLE_FONTS
from .icon_fonts import (
    IconFontRegistry,
    IconFontError,
    ICON_PRESETS,
    get_icon_preset
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
    '--google-font', '-g',
    type=str,
    help='Download font from Google Fonts (e.g., "Roboto", "Open Sans")'
)
@click.option(
    '--google-variant',
    type=str,
    default='regular',
    help='Google Font variant (regular, bold, italic, etc.)'
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
    '--icon-font',
    type=click.Choice(['material', 'fontawesome', 'fa'], case_sensitive=False),
    help='Use icon font (material, fontawesome)'
)
@click.option(
    '--icons',
    type=str,
    help='Icon names (comma-separated) or preset (navigation, actions, media, etc.)'
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
@click.option(
    '--list-google-fonts',
    is_flag=True,
    help='List popular Google Fonts'
)
@click.option(
    '--list-icon-fonts',
    is_flag=True,
    help='List supported icon fonts'
)
@click.option(
    '--list-icon-presets',
    is_flag=True,
    help='List available icon presets'
)
@click.version_option(version='0.2.0', prog_name='minifont')
def main(
    font: Optional[Path],
    google_font: Optional[str],
    google_variant: str,
    size: int,
    charset: Optional[str],
    icon_font: Optional[str],
    icons: Optional[str],
    output_format: Optional[str],
    output: Optional[Path],
    preview: bool,
    list_presets: bool,
    list_google_fonts: bool,
    list_icon_fonts: bool,
    list_icon_presets: bool
):
    """Minifont - Convert fonts to 1-bit bitmaps for Arduino and embedded projects.

    Run without arguments for interactive mode.
    """
    # Handle list flags
    if list_presets:
        print_info("Available character set presets:")
        for preset in Charset.get_all_presets():
            start, end = Charset.PRESETS[preset]
            print(f"  • {preset}: characters {start}-{end}")
        return

    if list_google_fonts:
        print_info("Popular Google Fonts:")
        for gfont in POPULAR_GOOGLE_FONTS:
            print(f"  • {gfont}")
        print("\nUse: minifont --google-font \"Font Name\" ...")
        return

    if list_icon_fonts:
        print_info("Supported icon fonts:")
        for ifont in IconFontRegistry.list_icon_fonts():
            print(f"  • {ifont}")
        print("\nUse: minifont --icon-font material --icons \"home,menu,search\" ...")
        return

    if list_icon_presets:
        print_info("Available icon presets:")
        for preset, icons in ICON_PRESETS.items():
            print(f"  • {preset}: {', '.join(icons[:5])}...")
        print("\nUse: minifont --icon-font material --icons navigation ...")
        return

    # Interactive mode if no arguments provided
    if not font and not google_font and not icon_font:
        interactive_mode()
        return

    # Determine font source
    font_path = None

    if google_font:
        # Download from Google Fonts
        try:
            print_info(f"Downloading Google Font: {google_font} ({google_variant})")
            downloader = GoogleFontsDownloader()
            font_path = Path(downloader.download_font(google_font, google_variant))
            print_success(f"Downloaded: {font_path}")
        except GoogleFontsError as e:
            print_error(str(e))
            sys.exit(1)
    elif font:
        font_path = font
    elif icon_font:
        # Icon font handling will be done in process_font
        pass
    else:
        print_error("Specify --font, --google-font, or --icon-font")
        sys.exit(1)

    # Batch mode
    if icon_font:
        # Icon font mode
        if not icons:
            print_error("--icons is required with --icon-font")
            sys.exit(1)

        if not output_format:
            print_error("--format is required in batch mode")
            sys.exit(1)

        try:
            process_icon_font(icon_font, icons, size, output_format, output, preview)
        except (IconFontError, RasterizerError, ExporterError) as e:
            print_error(str(e))
            sys.exit(1)
    else:
        # Regular font mode
        if not charset:
            print_error("--charset is required in batch mode")
            sys.exit(1)

        if not output_format:
            print_error("--format is required in batch mode")
            sys.exit(1)

        try:
            process_font(font_path, size, charset, output_format, output, preview)
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


def process_icon_font(
    icon_font_name: str,
    icons_input: str,
    size: int,
    output_format: str,
    output_path: Optional[Path],
    preview: bool
):
    """Process icon font conversion with given parameters."""

    print_info(f"Using icon font: {icon_font_name}")

    # Get icon font
    icon_font = IconFontRegistry.get_icon_font(icon_font_name)

    # Parse icons input (preset or comma-separated list)
    char_codes = set()

    if icons_input in ICON_PRESETS:
        # Use preset
        print_info(f"Using icon preset: {icons_input}")
        char_codes = get_icon_preset(icons_input, icon_font_name)
    else:
        # Parse comma-separated icon names
        icon_names = [name.strip() for name in icons_input.split(',')]
        print_info(f"Processing {len(icon_names)} icons")

        for icon_name in icon_names:
            try:
                code = icon_font.get_icon_code(icon_name)
                char_codes.add(code)
            except IconFontError as e:
                print_warning(str(e))

    if not char_codes:
        raise IconFontError("No valid icons found")

    print_success(f"Selected {len(char_codes)} icons")

    # For icon fonts, we need to use a font file that contains these icons
    # User should provide the font file separately or download it
    print_warning(
        f"Note: Make sure you have the {icon_font_name} font file installed.\n"
        f"For Material Icons: download from https://fonts.google.com/icons\n"
        f"For Font Awesome: download from https://fontawesome.com/"
    )

    # Ask user for font file path
    font_path_str = click.prompt(
        click.style(f"Path to {icon_font_name} font file", fg='yellow'),
        type=str
    )
    font_path = Path(font_path_str)

    if not font_path.exists():
        raise IconFontError(f"Font file not found: {font_path}")

    # Now process like a regular font
    print_info(f"Rasterizing icons at {size}px...")
    rasterizer = FontRasterizer(str(font_path), size)
    glyphs = rasterizer.rasterize_charset(char_codes)

    if not glyphs:
        raise RasterizerError("No icons could be rasterized")

    print_success(f"Rasterized {len(glyphs)} icons")

    # Show preview if requested
    if preview:
        click.echo()
        print_info("Icon preview (first 3):")
        click.echo()
        for glyph in glyphs[:3]:
            preview_text = rasterizer.preview_glyph(glyph)
            click.echo(preview_text)
            click.echo()

    # Export
    if output_path is None:
        ext = EXPORT_FORMATS[output_format][0]
        output_path = Path(f"{icon_font_name}_icons{size}{ext}")

    print_info(f"Exporting to {output_format} format: {output_path}")

    exporter_class = EXPORT_FORMATS[output_format][1]
    font_name = f"{icon_font_name.title()}Icons"
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
