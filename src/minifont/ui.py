"""Enhanced UI utilities using Rich for beautiful terminal output."""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.layout import Layout
from rich.text import Text
from rich.box import ROUNDED, DOUBLE, SIMPLE, HEAVY
from rich import box

from .font_discovery import FontInfo
from .rasterizer import GlyphBitmap


# Global console instance
console = Console()


def print_header():
    """Print application header with Rich formatting."""
    header_text = Text()
    header_text.append("╔═══════════════════════════════════════╗\n", style="bold cyan")
    header_text.append("║         ", style="bold cyan")
    header_text.append("Minifont v0.2.0", style="bold yellow")
    header_text.append("              ║\n", style="bold cyan")
    header_text.append("║  ", style="bold cyan")
    header_text.append("Font to Bitmap Converter for Arduino", style="cyan")
    header_text.append("║\n", style="bold cyan")
    header_text.append("╚═══════════════════════════════════════╝", style="bold cyan")

    console.print(header_text)
    console.print()


def show_fonts_table(fonts: List[FontInfo], title: str = "Available Fonts") -> None:
    """Display fonts in a beautiful table.

    Args:
        fonts: List of FontInfo objects
        title: Table title
    """
    if not fonts:
        console.print("[yellow]No fonts found[/yellow]")
        return

    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        box=ROUNDED,
        show_header=True,
        header_style="bold magenta",
        title_style="bold cyan"
    )

    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Filename", style="cyan", no_wrap=True)
    table.add_column("Font Name", style="green")
    table.add_column("Format", style="blue", justify="center")
    table.add_column("Size", style="yellow", justify="right")

    for i, font in enumerate(fonts, 1):
        size_str = f"{font.size_kb:.1f} KB"

        # Color code by format
        format_color = {
            'TTF': 'blue',
            'OTF': 'magenta',
            'WOFF': 'cyan',
            'WOFF2': 'green'
        }.get(font.format, 'white')

        table.add_row(
            str(i),
            font.filename,
            font.font_name or "Unknown",
            f"[{format_color}]{font.format}[/{format_color}]",
            size_str
        )

    console.print(table)
    console.print()


def show_fonts_grouped(fonts: List[FontInfo], families: dict) -> None:
    """Display fonts grouped by family with panels.

    Args:
        fonts: List of all fonts
        families: Dictionary of fonts grouped by family
    """
    console.print(f"[bold cyan]Found {len(fonts)} font(s) in {len(families)} families[/bold cyan]\n")

    for family_name, family_fonts in sorted(families.items()):
        # Create a table for each family
        table = Table(box=SIMPLE, show_header=False, pad_edge=False)
        table.add_column("File", style="cyan")
        table.add_column("Format", style="blue", justify="center")
        table.add_column("Size", style="yellow", justify="right")

        for font in family_fonts:
            table.add_row(
                font.filename,
                font.format,
                f"{font.size_kb:.1f} KB"
            )

        panel = Panel(
            table,
            title=f"[bold green]📁 {family_name}[/bold green]",
            border_style="green",
            box=ROUNDED
        )
        console.print(panel)


def show_glyph_preview(glyph: GlyphBitmap, char_on: str = "█", char_off: str = "·") -> Panel:
    """Create a rich panel with glyph preview.

    Args:
        glyph: GlyphBitmap to preview
        char_on: Character for set bits
        char_off: Character for unset bits

    Returns:
        Rich Panel with the preview
    """
    if glyph.width == 0 or glyph.height == 0:
        return Panel(
            "[dim]Empty glyph[/dim]",
            title=f"[cyan]'{glyph.char}' (U+{glyph.char_code:04X})[/cyan]",
            border_style="yellow"
        )

    # Generate bitmap display
    lines = []
    byte_index = 0

    for y in range(glyph.height):
        row = ""
        for x in range(glyph.width):
            byte_pos = byte_index + (x // 8)
            bit_pos = 7 - (x % 8)

            if byte_pos < len(glyph.bitmap):
                bit_set = (glyph.bitmap[byte_pos] >> bit_pos) & 1
                row += f"[bold white]{char_on}[/bold white]" if bit_set else f"[dim]{char_off}[/dim]"
            else:
                row += f"[dim]{char_off}[/dim]"

        lines.append(row)
        # Use pitch from glyph instead of calculating
        byte_index += glyph.pitch

    preview = "\n".join(lines)

    info = (
        f"[cyan]Character:[/cyan] '{glyph.char}' (U+{glyph.char_code:04X})\n"
        f"[cyan]Size:[/cyan] {glyph.width}×{glyph.height} px\n"
        f"[cyan]Advance:[/cyan] {glyph.advance_x} px"
    )

    return Panel(
        f"{info}\n\n{preview}",
        title=f"[bold cyan]Glyph Preview[/bold cyan]",
        border_style="cyan",
        box=ROUNDED
    )


def show_glyphs_comparison(glyphs: List[GlyphBitmap], max_glyphs: int = 3) -> None:
    """Show multiple glyph previews side by side.

    Args:
        glyphs: List of glyphs to preview
        max_glyphs: Maximum number to show
    """
    if not glyphs:
        console.print("[yellow]No glyphs to preview[/yellow]")
        return

    console.print(f"\n[bold cyan]Bitmap Preview (first {min(len(glyphs), max_glyphs)} characters)[/bold cyan]\n")

    # Show up to max_glyphs side by side
    panels = []
    for glyph in glyphs[:max_glyphs]:
        panels.append(show_glyph_preview(glyph))

    if len(panels) <= 2:
        # Show side by side
        columns = Columns(panels, equal=True, expand=True)
        console.print(columns)
    else:
        # Show in grid
        for panel in panels:
            console.print(panel)

    console.print()


def show_conversion_summary(
    font_name: str,
    char_count: int,
    glyph_count: int,
    output_file: str,
    file_size: int,
    format_type: str
) -> None:
    """Show conversion summary in a nice panel.

    Args:
        font_name: Name of the font
        char_count: Number of characters requested
        glyph_count: Number of glyphs rasterized
        output_file: Output file path
        file_size: Output file size in bytes
        format_type: Export format type
    """
    summary = Table(box=None, show_header=False, padding=(0, 2))
    summary.add_column("Label", style="cyan", no_wrap=True)
    summary.add_column("Value", style="green")

    summary.add_row("Font", font_name)
    summary.add_row("Characters Requested", str(char_count))
    summary.add_row("Glyphs Rasterized", str(glyph_count))
    summary.add_row("Export Format", format_type.upper())
    summary.add_row("Output File", output_file)
    summary.add_row("File Size", f"{file_size:,} bytes ({file_size/1024:.1f} KB)")

    panel = Panel(
        summary,
        title="[bold green]✓ Conversion Complete[/bold green]",
        border_style="green",
        box=DOUBLE
    )

    console.print(panel)


def show_progress_spinner(message: str):
    """Create a progress spinner context.

    Args:
        message: Message to display

    Returns:
        Progress context manager
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    )


def show_info(message: str) -> None:
    """Show info message."""
    console.print(f"[cyan]ℹ[/cyan] {message}")


def show_success(message: str) -> None:
    """Show success message."""
    console.print(f"[green]✓[/green] {message}")


def show_warning(message: str) -> None:
    """Show warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def show_error(message: str) -> None:
    """Show error message."""
    console.print(f"[red]✗[/red] {message}", style="bold red")


def show_code_preview(code: str, language: str = "c", title: str = "Generated Code Preview") -> None:
    """Show syntax-highlighted code preview.

    Args:
        code: Code to display
        language: Programming language for syntax highlighting
        title: Preview title
    """
    syntax = Syntax(
        code,
        language,
        theme="monokai",
        line_numbers=True,
        word_wrap=False
    )

    panel = Panel(
        syntax,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        box=ROUNDED
    )

    console.print(panel)


def create_menu_panel(title: str, options: List[str]) -> Panel:
    """Create a formatted menu panel.

    Args:
        title: Menu title
        options: List of menu options

    Returns:
        Rich Panel with menu
    """
    menu_text = "\n".join([f"  [cyan]•[/cyan] {opt}" for opt in options])

    return Panel(
        menu_text,
        title=f"[bold yellow]{title}[/bold yellow]",
        border_style="yellow",
        box=ROUNDED
    )


def create_font_sample_text(font_name: str) -> str:
    """Create a sample text showing the font name.

    Args:
        font_name: Name of the font

    Returns:
        Sample text
    """
    # Try to show some characters as preview
    sample = "AaBbCc 123"
    return f"[cyan]{font_name}[/cyan]\n[dim]{sample}[/dim]"


def create_parameters_panel(params: dict) -> Panel:
    """Create a panel showing current parameters.

    Args:
        params: Dictionary of parameters

    Returns:
        Rich Panel with parameters
    """
    table = Table(box=None, show_header=False, padding=(0, 1))
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="yellow")

    param_labels = {
        'font': '📁 Font',
        'size': '📏 Size',
        'charset': '🔤 Charset',
        'format': '💾 Format',
        'output': '📄 Output'
    }

    for key, value in params.items():
        label = param_labels.get(key, key)
        table.add_row(label, str(value))

    return Panel(
        table,
        title="[bold cyan]⚙️  Parameters[/bold cyan]",
        border_style="cyan",
        box=ROUNDED
    )


def show_interactive_interface(fonts: List[FontInfo], directory: str) -> None:
    """Show the main interactive interface.

    Args:
        fonts: List of available fonts
        directory: Directory path
    """
    console.clear()
    print_header()

    # Create fonts table
    if fonts:
        show_fonts_table(fonts[:15], f"Fonts in {directory}")
        if len(fonts) > 15:
            console.print(f"[dim]... and {len(fonts) - 15} more fonts[/dim]\n")
    else:
        console.print("[yellow]⚠[/yellow] No fonts found in current directory\n")
        console.print("[dim]Place TTF/OTF font files in this directory or specify a different path[/dim]\n")

    # Show controls
    controls = Panel(
        "[cyan]Controls:[/cyan]\n"
        "  • [green]↑/↓[/green] Navigate options\n"
        "  • [green]Enter[/green] Select\n"
        "  • [green]Esc[/green] Cancel/Back\n"
        "  • [green]Ctrl+C[/green] Exit",
        title="[bold yellow]ℹ️  How to Use[/bold yellow]",
        border_style="yellow",
        box=ROUNDED
    )
    console.print(controls)
