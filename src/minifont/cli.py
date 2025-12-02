"""Command-line interface for Minifont."""

import sys
import click
import questionary
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
from .font_discovery import FontDiscovery
from . import ui
from .tui import run_tui


EXPORT_FORMATS = {
    'c-header': ('.h', CHeaderExporter),
    'xbm': ('.xbm', XBMExporter),
    'bdf': ('.bdf', BDFExporter),
    'python': ('.py', PythonExporter),
}


def print_success(message: str) -> None:
    """Print success message in green."""
    ui.show_success(message)


def print_error(message: str) -> None:
    """Print error message in red."""
    ui.show_error(message)


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    ui.show_warning(message)


def print_info(message: str) -> None:
    """Print info message in cyan."""
    ui.show_info(message)


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
@click.option(
    '--list-fonts',
    is_flag=True,
    help='List font files in current directory'
)
@click.option(
    '--directory', '-d',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default='.',
    help='Directory to search for fonts (default: current directory)'
)
@click.option(
    '--no-tui',
    is_flag=True,
    help='Disable TUI and use wizard mode'
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
    list_icon_presets: bool,
    list_fonts: bool,
    directory: Path,
    no_tui: bool
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

    if list_fonts:
        # List fonts in directory with Rich table
        print_info(f"Searching for fonts in: {directory.resolve()}")
        fonts = FontDiscovery.find_fonts_in_directory(str(directory))

        if not fonts:
            print_warning(f"No font files found in {directory}")
            print_info("Supported formats: TTF, OTF, WOFF, WOFF2")
            return

        # Group by family if there are many fonts
        if len(fonts) > 10:
            families = FontDiscovery.group_fonts_by_family(fonts)
            ui.show_fonts_grouped(fonts, families)
        else:
            ui.show_fonts_table(fonts, f"Fonts in {directory.name if directory.name != '.' else 'Current Directory'}")

        ui.console.print("[dim]Use: minifont --font <filename> ...[/dim]\n")
        return

    # Interactive mode if no arguments provided
    if not font and not google_font and not icon_font:
        if no_tui:
            # Use wizard mode
            interactive_mode(directory)
        else:
            # Use TUI mode (default)
            run_tui(directory)
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


def interactive_mode(directory: Path = Path('.')):
    """Run in interactive mode with rich interface.

    Args:
        directory: Directory to search for fonts
    """
    try:
        # Discover fonts in directory
        with ui.show_progress_spinner("Scanning directory...") as progress:
            task = progress.add_task("Scanning", total=None)
            discovered_fonts = FontDiscovery.find_fonts_in_directory(str(directory))
            progress.stop()

        # Show the main interface
        ui.show_interactive_interface(discovered_fonts, str(directory.resolve()))

        # Start conversion workflow
        while True:
            ui.console.print()
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    questionary.Choice("🔄 Convert a font", "convert"),
                    questionary.Choice("🔄 Refresh font list", "refresh"),
                    questionary.Choice("🚪 Exit", "exit"),
                ]
            ).ask()

            if action is None or action == "exit":
                ui.console.print("\n[dim]Goodbye![/dim]\n")
                return

            if action == "refresh":
                # Refresh and show interface again
                with ui.show_progress_spinner("Scanning directory...") as progress:
                    task = progress.add_task("Scanning", total=None)
                    discovered_fonts = FontDiscovery.find_fonts_in_directory(str(directory))
                    progress.stop()
                ui.show_interactive_interface(discovered_fonts, str(directory.resolve()))
                continue

            if action == "convert":
                result = font_conversion_wizard_with_preview(directory, discovered_fonts)
                if result:
                    # Ask if user wants to continue
                    ui.console.print()
                    continue_choice = questionary.confirm(
                        "Convert another font?",
                        default=True
                    ).ask()
                    if not continue_choice:
                        ui.console.print("\n[dim]Goodbye![/dim]\n")
                        return
                continue

    except KeyboardInterrupt:
        ui.console.print("\n\n[dim]Cancelled by user[/dim]\n")
        sys.exit(0)


def font_conversion_wizard_with_preview(directory: Path, discovered_fonts: list):
    """Run font conversion with parameter configuration and preview.

    Args:
        directory: Directory to search for fonts
        discovered_fonts: List of discovered fonts

    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        ui.console.print()
        ui.console.print("[bold cyan]═══ Font Conversion Wizard ═══[/bold cyan]\n")

        # Step 1: Select font
        if not discovered_fonts:
            print_warning("No fonts found in current directory")
            font_path_str = questionary.path(
                "Enter font file path:",
                only_directories=False
            ).ask()
            if not font_path_str:
                return False
            font_path = Path(font_path_str)
        else:
            choices = [
                questionary.Choice(
                    title=f"{font.filename} - {font.font_name} ({font.format})",
                    value=font.path
                )
                for font in discovered_fonts
            ]
            font_path = questionary.select(
                "📁 Select a font:",
                choices=choices
            ).ask()
            if not font_path:
                return False

        # Step 2: Configure parameters
        ui.console.print()
        font_size = questionary.select(
            "📏 Select font size:",
            choices=[
                questionary.Choice("8 px", 8),
                questionary.Choice("12 px", 12),
                questionary.Choice("16 px (recommended)", 16),
                questionary.Choice("24 px", 24),
                questionary.Choice("32 px", 32),
            ],
            default=16
        ).ask()
        if font_size is None:
            return False

        ui.console.print()
        charset_input = questionary.select(
            "🔤 Select character set:",
            choices=[
                questionary.Choice("ascii - Basic ASCII (32-126)", "ascii"),
                questionary.Choice("extended - Extended ASCII (32-255)", "extended"),
                questionary.Choice("digits - Numbers 0-9", "digits"),
            ],
            default="ascii"
        ).ask()
        if charset_input is None:
            return False

        ui.console.print()
        output_format = questionary.select(
            "💾 Select export format:",
            choices=[
                questionary.Choice("c-header - C array (Adafruit GFX)", "c-header"),
                questionary.Choice("xbm - X BitMap (U8g2)", "xbm"),
                questionary.Choice("bdf - Bitmap Distribution Format", "bdf"),
                questionary.Choice("python - Python arrays", "python"),
            ],
            default="c-header"
        ).ask()
        if output_format is None:
            return False

        # Show parameters summary
        ui.console.print()
        params = {
            'font': Path(font_path).name,
            'size': f"{font_size} px",
            'charset': charset_input,
            'format': output_format
        }
        ui.console.print(ui.create_parameters_panel(params))

        # Step 3: Generate preview
        ui.console.print()
        show_preview = questionary.confirm(
            "🔍 Generate preview before conversion?",
            default=True
        ).ask()

        if show_preview:
            ui.console.print()
            print_info("Generating preview...")

            # Load font and generate preview
            try:
                loader = FontLoader(str(font_path))
                loader.validate()
                font_name = loader.get_font_name()

                # Parse charset
                if charset_input.lower() in Charset.get_all_presets():
                    char_codes = Charset.get_preset(charset_input.lower())
                else:
                    char_codes = Charset.parse_range(charset_input)

                # Filter to available
                available = loader.get_available_characters()
                available_chars = Charset.filter_available(char_codes, available)

                # Rasterize a few sample glyphs for preview
                sample_chars = list(available_chars)[:5]
                rasterizer = FontRasterizer(str(font_path), font_size)
                sample_glyphs = rasterizer.rasterize_charset(sample_chars)

                if sample_glyphs:
                    ui.console.print()
                    ui.show_glyphs_comparison(sample_glyphs, max_glyphs=3)
                else:
                    print_warning("No glyphs could be generated for preview")

            except Exception as e:
                print_error(f"Preview failed: {e}")
                return False

        # Step 4: Confirm and convert
        ui.console.print()
        proceed = questionary.confirm(
            "✓ Proceed with conversion?",
            default=True
        ).ask()

        if not proceed:
            print_info("Conversion cancelled")
            return False

        # Get output path
        default_ext = EXPORT_FORMATS[output_format][0]
        default_output = f"font_output{default_ext}"
        output_path_str = questionary.text(
            "📄 Output file path:",
            default=default_output
        ).ask()
        if not output_path_str:
            return False

        output_path = Path(output_path_str)

        # Perform conversion
        ui.console.print()
        ui.console.print("[bold cyan]Processing...[/bold cyan]\n")
        process_font(font_path, font_size, charset_input, output_format, output_path, False)

        return True

    except KeyboardInterrupt:
        ui.console.print("\n\n[dim]Cancelled[/dim]\n")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False




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

    # Rasterize glyphs with progress
    with ui.show_progress_spinner(f"Rasterizing glyphs at {size}px...") as progress:
        task = progress.add_task("Rasterizing", total=None)
        rasterizer = FontRasterizer(str(font_path), size)
        glyphs = rasterizer.rasterize_charset(available_chars)
        progress.stop()

    if not glyphs:
        raise RasterizerError("No glyphs could be rasterized")

    print_success(f"Rasterized {len(glyphs)} glyphs")

    # Show preview if requested
    if preview:
        ui.console.print()
        ui.show_glyphs_comparison(glyphs, max_glyphs=3)

    # Export
    if output_path is None:
        ext = EXPORT_FORMATS[output_format][0]
        output_path = Path(f"{font_name.lower()}{size}{ext}")

    print_info(f"Exporting to {output_format} format: {output_path}")

    exporter_class = EXPORT_FORMATS[output_format][1]
    exporter = exporter_class(font_name, size) if output_format == 'bdf' else exporter_class(font_name)
    exporter.export(glyphs, str(output_path))

    print_success(f"Export complete: {output_path}")

    # Show conversion summary
    file_size = output_path.stat().st_size
    ui.show_conversion_summary(
        font_name=font_name,
        char_count=len(char_codes),
        glyph_count=len(glyphs),
        output_file=str(output_path),
        file_size=file_size,
        format_type=output_format
    )


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
