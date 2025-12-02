"""Textual TUI (Text User Interface) for Minifont."""

import os
from pathlib import Path
from typing import List, Optional, Tuple
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label, Button, Select
from textual.binding import Binding
from textual.reactive import reactive
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .font_discovery import FontDiscovery, FontInfo
from .font_loader import FontLoader
from .charset import Charset
from .rasterizer import FontRasterizer, GlyphBitmap
from .exporters import CHeaderExporter, XBMExporter, BDFExporter, PythonExporter


EXPORT_FORMATS = {
    'c-header': ('.h', CHeaderExporter),
    'xbm': ('.xbm', XBMExporter),
    'bdf': ('.bdf', BDFExporter),
    'python': ('.py', PythonExporter),
}


class DirectoryInfoPanel(Static):
    """Panel showing current directory."""

    DEFAULT_CSS = """
    DirectoryInfoPanel {
        height: 3;
        background: $surface;
        border: solid $primary;
        padding: 0 2;
    }
    """

    current_dir = reactive(Path("."))

    def __init__(self, directory: Path) -> None:
        super().__init__()
        self.current_dir = directory.resolve()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label(f"[bold cyan]📂 Current Directory:[/bold cyan] [yellow]{self.current_dir}[/yellow]")

    def update_directory(self, new_dir: Path) -> None:
        """Update current directory display."""
        self.current_dir = new_dir.resolve()
        self.refresh(recompose=True)


class FileBrowserPanel(ScrollableContainer):
    """Panel for browsing directories and fonts."""

    DEFAULT_CSS = """
    FileBrowserPanel {
        border: solid cyan;
        height: 100%;
        padding: 1;
    }
    """

    def __init__(self, directory: Path) -> None:
        super().__init__()
        self.current_dir = directory.resolve()
        self.items: List[Tuple[str, Path, bool]] = []  # (name, path, is_dir)
        self.selected_index = 0
        self.fonts: List[FontInfo] = []
        self.load_directory()

    def load_directory(self) -> None:
        """Load contents of current directory."""
        self.items = []

        # Add parent directory if not at root
        if self.current_dir.parent != self.current_dir:
            self.items.append(("📁 ..", self.current_dir.parent, True))

        try:
            # Get all items in directory
            all_items = list(self.current_dir.iterdir())

            # Separate directories and files
            directories = sorted([d for d in all_items if d.is_dir()], key=lambda x: x.name.lower())
            files = sorted([f for f in all_items if f.is_file()], key=lambda x: x.name.lower())

            # Add directories first
            for d in directories:
                if not d.name.startswith('.'):  # Skip hidden directories
                    self.items.append((f"📁 {d.name}/", d, True))

            # Load fonts from current directory
            self.fonts = FontDiscovery.find_fonts_in_directory(str(self.current_dir))

            # Add font files
            font_paths = {font.path for font in self.fonts}
            for f in files:
                if f in font_paths:
                    # It's a font file
                    font_info = next((font for font in self.fonts if font.path == f), None)
                    if font_info:
                        self.items.append((f"🔤 {f.name}", f, False))

        except PermissionError:
            self.items.append(("❌ Permission denied", None, False))

        self.selected_index = 0

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        font_count = len([item for item in self.items if not item[2] and item[1]])
        dir_count = len([item for item in self.items if item[2]]) - (1 if len(self.items) > 0 and self.items[0][0] == "📁 .." else 0)

        yield Label("[bold cyan]📂 File Browser[/bold cyan]")
        yield Label(f"[dim]{dir_count} folders, {font_count} fonts - Press Enter to open[/dim]")
        yield Label("")  # Spacing

        if not self.items:
            yield Label("[yellow]Empty directory[/yellow]")
        else:
            for i, (name, path, is_dir) in enumerate(self.items):
                marker = "► " if i == self.selected_index else "  "
                if i == self.selected_index:
                    yield Label(f"{marker}[bold cyan]{name}[/bold cyan]")
                else:
                    yield Label(f"{marker}{name}")

    def select_next(self) -> None:
        """Select next item."""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)
            self.refresh(recompose=True)
            try:
                self.scroll_to_widget(self.query(Label)[self.selected_index + 3])
            except:
                pass

    def select_previous(self) -> None:
        """Select previous item."""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)
            self.refresh(recompose=True)
            try:
                self.scroll_to_widget(self.query(Label)[self.selected_index + 3])
            except:
                pass

    def get_selected_item(self) -> Optional[Tuple[str, Path, bool]]:
        """Get currently selected item."""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def get_selected_font(self) -> Optional[FontInfo]:
        """Get currently selected font if it's a font file."""
        item = self.get_selected_item()
        if item and not item[2] and item[1]:  # Not a directory
            # Find the font info
            for font in self.fonts:
                if font.path == item[1]:
                    return font
        return None

    def enter_directory(self, new_dir: Path) -> None:
        """Navigate to a new directory."""
        if new_dir.is_dir():
            self.current_dir = new_dir.resolve()
            self.load_directory()
            self.refresh(recompose=True)


class ParametersPanel(Static):
    """Panel for configuring conversion parameters."""

    DEFAULT_CSS = """
    ParametersPanel {
        border: solid yellow;
        height: 100%;
        padding: 1;
    }
    """

    font_size = reactive(16)
    charset = reactive("ascii")
    output_format = reactive("c-header")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold yellow]⚙️  Parameters[/bold yellow]")
        yield Label("")
        yield Label(f"[cyan]Size:[/cyan] [yellow]{self.font_size} px[/yellow]")
        yield Label(f"[cyan]Charset:[/cyan] [yellow]{self.charset}[/yellow]")
        yield Label(f"[cyan]Format:[/cyan] [yellow]{self.output_format}[/yellow]")
        yield Label("")
        yield Label("[dim]Use +/- to change size[/dim]")
        yield Label("[dim]Use c to change charset[/dim]")
        yield Label("[dim]Use f to change format[/dim]")

    def increase_size(self) -> None:
        """Increase font size."""
        sizes = [8, 12, 16, 20, 24, 32, 48, 64]
        current_idx = sizes.index(self.font_size) if self.font_size in sizes else 2
        if current_idx < len(sizes) - 1:
            self.font_size = sizes[current_idx + 1]
            self.refresh(recompose=True)

    def decrease_size(self) -> None:
        """Decrease font size."""
        sizes = [8, 12, 16, 20, 24, 32, 48, 64]
        current_idx = sizes.index(self.font_size) if self.font_size in sizes else 2
        if current_idx > 0:
            self.font_size = sizes[current_idx - 1]
            self.refresh(recompose=True)

    def cycle_charset(self) -> None:
        """Cycle through charset options."""
        charsets = ["ascii", "extended", "digits", "uppercase", "lowercase"]
        current_idx = charsets.index(self.charset) if self.charset in charsets else 0
        self.charset = charsets[(current_idx + 1) % len(charsets)]
        self.refresh(recompose=True)

    def cycle_format(self) -> None:
        """Cycle through format options."""
        formats = ["c-header", "xbm", "bdf", "python"]
        current_idx = formats.index(self.output_format) if self.output_format in formats else 0
        self.output_format = formats[(current_idx + 1) % len(formats)]
        self.refresh(recompose=True)


class PreviewPanel(ScrollableContainer):
    """Panel for bitmap preview."""

    DEFAULT_CSS = """
    PreviewPanel {
        border: solid green;
        height: 100%;
        padding: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.preview_glyphs: List[GlyphBitmap] = []

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold green]🔍 Preview[/bold green]")
        yield Label("[dim](Scroll with mouse or arrow keys)[/dim]")

        if not self.preview_glyphs:
            yield Label("\n[dim]Select a font and press 'p' to preview[/dim]")
        else:
            yield Label(f"[bold green]Showing {len(self.preview_glyphs)} characters[/bold green]\n")
            for glyph in self.preview_glyphs:
                yield Label(self._render_glyph(glyph))

    def _render_glyph(self, glyph: GlyphBitmap) -> str:
        """Render glyph as text with better formatting."""
        if glyph.width == 0 or glyph.height == 0:
            return f"[dim]'{glyph.char}' (U+{glyph.char_code:04X}) - Empty glyph[/dim]\n"

        # Header with character info
        lines = [
            f"[bold cyan]Character: '{glyph.char}' (U+{glyph.char_code:04X})[/bold cyan]",
            f"[dim]Size: {glyph.width}×{glyph.height} px | Advance: {glyph.advance_x} px[/dim]",
            ""
        ]

        # Render bitmap with box drawing
        byte_index = 0
        char_on = "██"  # Double width for better visibility
        char_off = "··"

        # Top border
        lines.append("┌" + "─" * (glyph.width * 2) + "┐")

        for y in range(min(glyph.height, 24)):  # Show up to 24 rows
            row = "│"
            for x in range(glyph.width):
                byte_pos = byte_index + (x // 8)
                bit_pos = 7 - (x % 8)

                if byte_pos < len(glyph.bitmap):
                    bit_set = (glyph.bitmap[byte_pos] >> bit_pos) & 1
                    if bit_set:
                        row += f"[bold white]{char_on}[/bold white]"
                    else:
                        row += f"[dim]{char_off}[/dim]"
                else:
                    row += f"[dim]{char_off}[/dim]"

            row += "│"
            lines.append(row)
            # Use pitch from glyph instead of calculating
            byte_index += glyph.pitch

        # Bottom border
        lines.append("└" + "─" * (glyph.width * 2) + "┘")
        lines.append("")  # Empty line between glyphs

        return "\n".join(lines)

    def update_preview(self, glyphs: List[GlyphBitmap]) -> None:
        """Update preview with new glyphs."""
        self.preview_glyphs = glyphs
        self.refresh(recompose=True)


class MinifontTUI(App):
    """Minifont Text User Interface."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #dir-info {
        dock: top;
    }

    #main-container {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 1fr 1fr;
        grid-columns: 1fr 1fr;
        height: 1fr;
    }

    #browser {
        row-span: 2;
    }

    #parameters {
        column-span: 1;
    }

    #preview {
        column-span: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up", "select_previous", "↑ Previous"),
        Binding("down", "select_next", "↓ Next"),
        Binding("enter", "open_item", "Open/Convert"),
        Binding("plus,equal", "increase_size", "+ Size"),
        Binding("minus,underscore", "decrease_size", "- Size"),
        Binding("c", "cycle_charset", "Charset"),
        Binding("f", "cycle_format", "Format"),
        Binding("p", "preview", "Preview"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, directory: Path = Path('.')):
        super().__init__()
        self.directory = directory
        self.dir_info_panel: Optional[DirectoryInfoPanel] = None
        self.browser_panel: Optional[FileBrowserPanel] = None
        self.params_panel: Optional[ParametersPanel] = None
        self.preview_panel: Optional[PreviewPanel] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header(show_clock=True)

        # Directory info panel at top
        self.dir_info_panel = DirectoryInfoPanel(self.directory)
        self.dir_info_panel.id = "dir-info"
        yield self.dir_info_panel

        # Main container with grid layout
        with Container(id="main-container"):
            # File browser
            self.browser_panel = FileBrowserPanel(self.directory)
            self.browser_panel.id = "browser"
            yield self.browser_panel

            # Parameters panel
            self.params_panel = ParametersPanel()
            self.params_panel.id = "parameters"
            yield self.params_panel

            # Preview panel
            self.preview_panel = PreviewPanel()
            self.preview_panel.id = "preview"
            yield self.preview_panel

        yield Footer()

    def action_select_next(self) -> None:
        """Select next item."""
        if self.browser_panel:
            self.browser_panel.select_next()

    def action_select_previous(self) -> None:
        """Select previous item."""
        if self.browser_panel:
            self.browser_panel.select_previous()

    def action_open_item(self) -> None:
        """Open directory or convert font."""
        if not self.browser_panel:
            return

        item = self.browser_panel.get_selected_item()
        if not item:
            return

        name, path, is_dir = item

        if is_dir and path:
            # Navigate to directory
            self.browser_panel.enter_directory(path)
            if self.dir_info_panel:
                self.dir_info_panel.update_directory(path)
            self.notify(f"Opened: {path.name}", severity="information")
        else:
            # It's a font - convert it
            self.action_convert()

    def action_increase_size(self) -> None:
        """Increase font size."""
        if self.params_panel:
            self.params_panel.increase_size()

    def action_decrease_size(self) -> None:
        """Decrease font size."""
        if self.params_panel:
            self.params_panel.decrease_size()

    def action_cycle_charset(self) -> None:
        """Cycle charset."""
        if self.params_panel:
            self.params_panel.cycle_charset()

    def action_cycle_format(self) -> None:
        """Cycle format."""
        if self.params_panel:
            self.params_panel.cycle_format()

    def action_preview(self) -> None:
        """Generate preview."""
        if not self.browser_panel or not self.params_panel or not self.preview_panel:
            return

        font = self.browser_panel.get_selected_font()
        if not font:
            self.notify("No font selected", severity="warning")
            return

        try:
            # Load font
            loader = FontLoader(str(font.path))
            loader.validate()

            # Get charset
            charset = self.params_panel.charset
            if charset.lower() in Charset.get_all_presets():
                char_codes = Charset.get_preset(charset.lower())
            else:
                char_codes = Charset.parse_range(charset)

            # Filter available
            available = loader.get_available_characters()
            available_chars = Charset.filter_available(char_codes, available)

            # Rasterize ALL characters for preview
            rasterizer = FontRasterizer(str(font.path), self.params_panel.font_size)
            glyphs = rasterizer.rasterize_charset(available_chars)

            # Update preview
            self.preview_panel.update_preview(glyphs)
            self.notify(f"Preview generated: {len(glyphs)} characters", severity="information")

        except Exception as e:
            self.notify(f"Preview failed: {str(e)}", severity="error")

    def action_convert(self) -> None:
        """Convert font."""
        if not self.browser_panel or not self.params_panel:
            return

        font = self.browser_panel.get_selected_font()
        if not font:
            self.notify("No font selected", severity="warning")
            return

        try:
            # Load font
            loader = FontLoader(str(font.path))
            loader.validate()
            font_name = loader.get_font_name()

            # Get charset
            charset = self.params_panel.charset
            if charset.lower() in Charset.get_all_presets():
                char_codes = Charset.get_preset(charset.lower())
            else:
                char_codes = Charset.parse_range(charset)

            # Filter available
            available = loader.get_available_characters()
            available_chars = Charset.filter_available(char_codes, available)

            # Rasterize
            rasterizer = FontRasterizer(str(font.path), self.params_panel.font_size)
            glyphs = rasterizer.rasterize_charset(available_chars)

            # Export - find unique filename
            output_format = self.params_panel.output_format
            ext = EXPORT_FORMATS[output_format][0]
            base_name = f"{font_name.lower()}_{self.params_panel.font_size}"
            output_path = Path(f"{base_name}{ext}")

            # Find unique filename if file exists
            counter = 1
            while output_path.exists():
                output_path = Path(f"{base_name}_{counter}{ext}")
                counter += 1

            exporter_class = EXPORT_FORMATS[output_format][1]
            exporter = exporter_class(font_name, self.params_panel.font_size) if output_format == 'bdf' else exporter_class(font_name)
            exporter.export(glyphs, str(output_path))

            self.notify(f"✓ Converted: {output_path}", severity="information", timeout=5)

        except Exception as e:
            self.notify(f"Conversion failed: {str(e)}", severity="error")

    def action_refresh(self) -> None:
        """Refresh current directory."""
        if self.browser_panel:
            self.browser_panel.load_directory()
            self.browser_panel.refresh(recompose=True)
            self.notify("Directory refreshed", severity="information")


def run_tui(directory: Path = Path('.')) -> None:
    """Run the Minifont TUI application.

    Args:
        directory: Directory to scan for fonts
    """
    app = MinifontTUI(directory)
    app.run()
