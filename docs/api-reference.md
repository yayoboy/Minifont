# API Reference

Complete API documentation for all Minifont modules.

## Table of Contents

- [Charset Module](#charset-module)
- [Font Loader Module](#font-loader-module)
- [Font Discovery Module](#font-discovery-module)
- [Rasterizer Module](#rasterizer-module)
- [Exporters Module](#exporters-module)
- [Google Fonts Module](#google-fonts-module)
- [Icon Fonts Module](#icon-fonts-module)
- [UI Module](#ui-module)

---

## Charset Module

**Module**: `minifont.charset`

### Class: Charset

Character set parsing and management.

#### Class Attributes

```python
PRESETS: Dict[str, Tuple[int, int]] = {
    'ascii': (32, 126),
    'extended': (32, 255),
    'digits': (48, 57),
    'uppercase': (65, 90),
    'lowercase': (97, 122)
}
```

#### Static Methods

##### `parse_range(range_str: str) -> set[int]`

Parse character range string to set of character codes.

**Parameters**:
- `range_str` (str): Range string (e.g., "32-126" or "32-90,160-255")

**Returns**:
- `set[int]`: Set of character codes

**Raises**:
- `CharsetError`: If range format is invalid

**Examples**:
```python
from minifont.charset import Charset

# Single range
codes = Charset.parse_range("65-90")  # {65, 66, ..., 90}

# Multiple ranges
codes = Charset.parse_range("32-126,160-255")

# Single character
codes = Charset.parse_range("65")  # {65}
```

##### `get_preset(name: str) -> set[int]`

Get character codes for a preset.

**Parameters**:
- `name` (str): Preset name ('ascii', 'extended', 'digits', etc.)

**Returns**:
- `set[int]`: Set of character codes

**Raises**:
- `CharsetError`: If preset doesn't exist

**Examples**:
```python
# Get ASCII preset
codes = Charset.get_preset('ascii')

# Get digits only
codes = Charset.get_preset('digits')
```

##### `get_all_presets() -> List[str]`

Get list of all available preset names.

**Returns**:
- `List[str]`: List of preset names

**Example**:
```python
presets = Charset.get_all_presets()
# ['ascii', 'extended', 'digits', 'uppercase', 'lowercase']
```

##### `filter_available(requested: set[int], available: set[int]) -> set[int]`

Filter requested characters to only those available in font.

**Parameters**:
- `requested` (set[int]): Requested character codes
- `available` (set[int]): Available character codes in font

**Returns**:
- `set[int]`: Intersection of requested and available

**Example**:
```python
requested = {65, 66, 67, 500}  # A, B, C, and invalid char
available = {65, 66, 67, 68}    # A, B, C, D
result = Charset.filter_available(requested, available)
# {65, 66, 67}
```

---

## Font Loader Module

**Module**: `minifont.font_loader`

### Class: FontLoader

Load and validate font files.

#### Constructor

```python
def __init__(self, font_path: str)
```

**Parameters**:
- `font_path` (str): Path to font file

**Example**:
```python
from minifont.font_loader import FontLoader

loader = FontLoader('myfont.ttf')
```

#### Methods

##### `validate() -> None`

Validate font file integrity.

**Raises**:
- `FontLoaderError`: If font is invalid or cannot be loaded

**Example**:
```python
try:
    loader.validate()
    print("Font is valid")
except FontLoaderError as e:
    print(f"Invalid font: {e}")
```

##### `get_font_name() -> str`

Extract font family name.

**Returns**:
- `str`: Font family name

**Example**:
```python
name = loader.get_font_name()
# "Arial"
```

##### `get_available_characters() -> set[int]`

Get set of available character codes in font.

**Returns**:
- `set[int]`: Character codes supported by font

**Example**:
```python
chars = loader.get_available_characters()
# {32, 33, 34, ..., 126}
```

---

## Font Discovery Module

**Module**: `minifont.font_discovery`

### Class: FontInfo

Font metadata container.

```python
@dataclass
class FontInfo:
    path: Path              # Full path to font file
    filename: str           # File name only
    font_name: str          # Font family name
    format: str             # 'TTF', 'OTF', 'WOFF', 'WOFF2'
    size_kb: float          # File size in KB
```

### Class: FontDiscovery

Font file discovery utilities.

#### Static Methods

##### `find_fonts_in_directory(directory: str, recursive: bool = False) -> List[FontInfo]`

Find all font files in directory.

**Parameters**:
- `directory` (str): Directory path to scan
- `recursive` (bool, optional): Search subdirectories. Default: False

**Returns**:
- `List[FontInfo]`: List of discovered fonts

**Example**:
```python
from minifont.font_discovery import FontDiscovery

# Search current directory
fonts = FontDiscovery.find_fonts_in_directory('.')

# Search recursively
fonts = FontDiscovery.find_fonts_in_directory('/fonts', recursive=True)

for font in fonts:
    print(f"{font.font_name} ({font.format}) - {font.size_kb:.1f} KB")
```

##### `group_fonts_by_family(fonts: List[FontInfo]) -> Dict[str, List[FontInfo]]`

Group fonts by family name.

**Parameters**:
- `fonts` (List[FontInfo]): List of fonts to group

**Returns**:
- `Dict[str, List[FontInfo]]`: Dictionary mapping family names to font lists

**Example**:
```python
fonts = FontDiscovery.find_fonts_in_directory('.')
families = FontDiscovery.group_fonts_by_family(fonts)

for family_name, family_fonts in families.items():
    print(f"{family_name}: {len(family_fonts)} variants")
```

---

## Rasterizer Module

**Module**: `minifont.rasterizer`

### Class: GlyphBitmap

Rasterized glyph data container.

```python
@dataclass
class GlyphBitmap:
    char_code: int          # Unicode code point
    width: int              # Bitmap width in pixels
    height: int             # Bitmap height in pixels
    advance_x: int          # Horizontal advance in pixels
    offset_x: int           # X offset from cursor
    offset_y: int           # Y offset from baseline
    bitmap: bytes           # Packed 1-bit bitmap data
    pitch: int              # Bytes per row (includes padding)

    @property
    def char(self) -> str:
        """Get character representation"""
```

### Class: FontRasterizer

Font rasterization engine.

#### Constructor

```python
def __init__(self, font_path: str, size: int = 16)
```

**Parameters**:
- `font_path` (str): Path to font file
- `size` (int, optional): Font size in pixels. Default: 16

**Example**:
```python
from minifont.rasterizer import FontRasterizer

rasterizer = FontRasterizer('myfont.ttf', size=16)
```

#### Methods

##### `rasterize_glyph(char_code: int) -> Optional[GlyphBitmap]`

Rasterize a single character.

**Parameters**:
- `char_code` (int): Unicode code point

**Returns**:
- `Optional[GlyphBitmap]`: Glyph bitmap or None if character unavailable

**Example**:
```python
# Rasterize 'A' (code 65)
glyph = rasterizer.rasterize_glyph(65)

if glyph:
    print(f"Character: {glyph.char}")
    print(f"Size: {glyph.width}×{glyph.height}")
    print(f"Advance: {glyph.advance_x}")
```

##### `rasterize_charset(char_codes: set[int]) -> List[GlyphBitmap]`

Rasterize multiple characters.

**Parameters**:
- `char_codes` (set[int]): Set of character codes to rasterize

**Returns**:
- `List[GlyphBitmap]`: List of successfully rasterized glyphs

**Example**:
```python
from minifont.charset import Charset

# Rasterize ASCII characters
char_codes = Charset.get_preset('ascii')
glyphs = rasterizer.rasterize_charset(char_codes)

print(f"Rasterized {len(glyphs)} glyphs")
```

##### `get_font_metrics() -> dict`

Get font metrics information.

**Returns**:
- `dict`: Dictionary with font metrics

**Example**:
```python
metrics = rasterizer.get_font_metrics()
print(metrics)
# {
#   'size': 16,
#   'height': 18,
#   'ascender': 14,
#   'descender': -4,
#   'max_advance': 16
# }
```

##### `preview_glyph(glyph: GlyphBitmap, char: str = '#', empty: str = '.') -> str`

Generate ASCII art preview of glyph.

**Parameters**:
- `glyph` (GlyphBitmap): Glyph to preview
- `char` (str, optional): Character for set bits. Default: '#'
- `empty` (str, optional): Character for unset bits. Default: '.'

**Returns**:
- `str`: Multi-line ASCII art representation

**Example**:
```python
glyph = rasterizer.rasterize_glyph(65)  # 'A'
preview = rasterizer.preview_glyph(glyph)
print(preview)
# Character: 'A' (U+0041)
# Size: 8x12, Advance: 8px
#
# ########
# #......#
# #......#
# ...
```

---

## Exporters Module

**Module**: `minifont.exporters`

### Base Class: BaseExporter

Abstract base class for all exporters.

#### Constructor

```python
def __init__(self, font_name: str = "CustomFont")
```

**Parameters**:
- `font_name` (str, optional): Name for exported font. Default: "CustomFont"

#### Methods

##### `export(glyphs: List[GlyphBitmap], output_path: str) -> None`

Export glyphs to file (must be implemented by subclasses).

**Parameters**:
- `glyphs` (List[GlyphBitmap]): Glyphs to export
- `output_path` (str): Output file path

**Raises**:
- `ExporterError`: If export fails

### Class: CHeaderExporter

Export to C header format (Adafruit GFX compatible).

**Example**:
```python
from minifont.exporters import CHeaderExporter

exporter = CHeaderExporter("MyFont")
exporter.export(glyphs, "myfont.h")
```

**Output Format**:
```c
const uint8_t MyFontBitmaps[] PROGMEM = { ... };
const GFXglyph MyFontGlyphs[] PROGMEM = { ... };
const GFXfont MyFont PROGMEM = { ... };
```

### Class: XBMExporter

Export to XBM format (U8g2 compatible).

**Example**:
```python
from minifont.exporters import XBMExporter

exporter = XBMExporter("MyFont")
exporter.export(glyphs, "myfont.xbm")
```

**Output Format**:
```c
#define MyFont_width 128
#define MyFont_height 16
static unsigned char MyFont_bits[] = { ... };
```

### Class: BDFExporter

Export to BDF (Bitmap Distribution Format).

**Constructor**:
```python
def __init__(self, font_name: str = "CustomFont", font_size: int = 16)
```

**Example**:
```python
from minifont.exporters import BDFExporter

exporter = BDFExporter("MyFont", font_size=16)
exporter.export(glyphs, "myfont.bdf")
```

### Class: PythonExporter

Export to Python byte arrays (MicroPython compatible).

**Example**:
```python
from minifont.exporters import PythonExporter

exporter = PythonExporter("MyFont")
exporter.export(glyphs, "myfont.py")
```

**Output Format**:
```python
MyFont_bitmaps = bytes([...])
MyFont_glyphs = [(...), ...]
```

---

## Google Fonts Module

**Module**: `minifont.google_fonts`

### Class: GoogleFontsDownloader

Download fonts from Google Fonts.

#### Methods

##### `download_font(font_name: str, variant: str = 'regular') -> str`

Download font from Google Fonts.

**Parameters**:
- `font_name` (str): Font family name (e.g., "Roboto")
- `variant` (str, optional): Font variant. Default: 'regular'

**Returns**:
- `str`: Path to downloaded font file

**Raises**:
- `GoogleFontsError`: If download fails

**Example**:
```python
from minifont.google_fonts import GoogleFontsDownloader

downloader = GoogleFontsDownloader()

# Download Roboto Regular
font_path = downloader.download_font("Roboto")

# Download Open Sans Bold
font_path = downloader.download_font("Open Sans", variant="bold")
```

### Constants

```python
POPULAR_GOOGLE_FONTS: List[str] = [
    "Roboto", "Open Sans", "Lato", "Montserrat",
    "Roboto Condensed", "Oswald", "Source Sans Pro",
    # ... more fonts
]
```

---

## Icon Fonts Module

**Module**: `minifont.icon_fonts`

### Class: IconFont

Icon font metadata and mappings.

```python
@dataclass
class IconFont:
    name: str                       # Icon font name
    unicode_map: Dict[str, int]     # Icon name → Unicode mapping

    def get_icon_code(self, icon_name: str) -> int:
        """Get Unicode code for icon name"""
```

### Class: IconFontRegistry

Icon font registry and management.

#### Static Methods

##### `get_icon_font(name: str) -> IconFont`

Get icon font by name.

**Parameters**:
- `name` (str): Icon font name ('material', 'fontawesome')

**Returns**:
- `IconFont`: Icon font object

**Raises**:
- `IconFontError`: If icon font not found

**Example**:
```python
from minifont.icon_fonts import IconFontRegistry

material = IconFontRegistry.get_icon_font('material')
home_code = material.get_icon_code('home')
```

##### `list_icon_fonts() -> List[str]`

Get list of supported icon fonts.

**Returns**:
- `List[str]`: Icon font names

**Example**:
```python
fonts = IconFontRegistry.list_icon_fonts()
# ['material', 'fontawesome']
```

### Functions

##### `get_icon_preset(preset_name: str, icon_font: str = 'material') -> set[int]`

Get icon codes for a preset.

**Parameters**:
- `preset_name` (str): Preset name
- `icon_font` (str, optional): Icon font. Default: 'material'

**Returns**:
- `set[int]`: Set of Unicode codes for icons

**Example**:
```python
from minifont.icon_fonts import get_icon_preset

# Get navigation icons
codes = get_icon_preset('navigation', 'material')
```

### Constants

```python
ICON_PRESETS: Dict[str, List[str]] = {
    'navigation': ['home', 'menu', 'arrow_back', 'arrow_forward', 'close'],
    'actions': ['add', 'remove', 'edit', 'delete', 'save', 'search'],
    'media': ['play_arrow', 'pause', 'stop', 'volume_up', 'volume_down'],
    # ... more presets
}
```

---

## UI Module

**Module**: `minifont.ui`

Rich terminal UI components and utilities.

### Global Instance

```python
console: Console  # Global Rich console instance
```

### Functions

##### `print_header() -> None`

Display application header with branding.

**Example**:
```python
from minifont import ui

ui.print_header()
```

##### `show_fonts_table(fonts: List[FontInfo], title: str = "Available Fonts") -> None`

Display fonts in formatted table.

**Parameters**:
- `fonts` (List[FontInfo]): List of fonts to display
- `title` (str, optional): Table title

**Example**:
```python
from minifont.font_discovery import FontDiscovery
from minifont import ui

fonts = FontDiscovery.find_fonts_in_directory('.')
ui.show_fonts_table(fonts, "Local Fonts")
```

##### `show_glyph_preview(glyph: GlyphBitmap, char_on: str = "█", char_off: str = "·") -> Panel`

Create Rich panel with glyph preview.

**Parameters**:
- `glyph` (GlyphBitmap): Glyph to preview
- `char_on` (str, optional): Character for set bits
- `char_off` (str, optional): Character for unset bits

**Returns**:
- `Panel`: Rich Panel object

**Example**:
```python
from minifont.rasterizer import FontRasterizer
from minifont import ui

rasterizer = FontRasterizer('font.ttf', 16)
glyph = rasterizer.rasterize_glyph(65)
panel = ui.show_glyph_preview(glyph)
ui.console.print(panel)
```

##### `show_glyphs_comparison(glyphs: List[GlyphBitmap], max_glyphs: int = 3) -> None`

Show multiple glyph previews side by side.

**Parameters**:
- `glyphs` (List[GlyphBitmap]): Glyphs to preview
- `max_glyphs` (int, optional): Maximum to display. Default: 3

**Example**:
```python
from minifont import ui

ui.show_glyphs_comparison(glyphs, max_glyphs=3)
```

##### `show_conversion_summary(...) -> None`

Display conversion results summary.

**Parameters**:
- `font_name` (str): Font name
- `char_count` (int): Number of characters requested
- `glyph_count` (int): Number of glyphs rasterized
- `output_file` (str): Output file path
- `file_size` (int): Output file size in bytes
- `format_type` (str): Export format

**Example**:
```python
from minifont import ui

ui.show_conversion_summary(
    font_name="Arial",
    char_count=95,
    glyph_count=95,
    output_file="arial16.h",
    file_size=12500,
    format_type="c-header"
)
```

##### Message Functions

```python
show_info(message: str) -> None
show_success(message: str) -> None
show_warning(message: str) -> None
show_error(message: str) -> None
```

Display colored status messages.

**Example**:
```python
from minifont import ui

ui.show_info("Processing font...")
ui.show_success("Conversion complete!")
ui.show_warning("Some characters unavailable")
ui.show_error("Font file not found")
```

---

## Complete Usage Example

```python
from minifont.font_loader import FontLoader
from minifont.charset import Charset
from minifont.rasterizer import FontRasterizer
from minifont.exporters import CHeaderExporter
from minifont import ui

# 1. Load font
loader = FontLoader('myfont.ttf')
loader.validate()
font_name = loader.get_font_name()

# 2. Parse character set
char_codes = Charset.get_preset('ascii')
available = loader.get_available_characters()
available_chars = Charset.filter_available(char_codes, available)

# 3. Rasterize glyphs
rasterizer = FontRasterizer('myfont.ttf', size=16)
glyphs = rasterizer.rasterize_charset(available_chars)

# 4. Preview
ui.show_glyphs_comparison(glyphs[:3])

# 5. Export
exporter = CHeaderExporter(font_name)
exporter.export(glyphs, 'output.h')

# 6. Summary
ui.show_success(f"Exported {len(glyphs)} glyphs to output.h")
```

---

## Error Handling

### Exception Classes

```python
class CharsetError(Exception):
    """Character set parsing errors"""

class FontLoaderError(Exception):
    """Font loading errors"""

class RasterizerError(Exception):
    """Rasterization errors"""

class ExporterError(Exception):
    """Export errors"""

class GoogleFontsError(Exception):
    """Google Fonts download errors"""

class IconFontError(Exception):
    """Icon font errors"""
```

### Best Practices

```python
try:
    # Font operations
    loader = FontLoader(font_path)
    loader.validate()
    glyphs = rasterizer.rasterize_charset(char_codes)
    exporter.export(glyphs, output_path)

except FontLoaderError as e:
    ui.show_error(f"Font error: {e}")
except RasterizerError as e:
    ui.show_error(f"Rasterization error: {e}")
except ExporterError as e:
    ui.show_error(f"Export error: {e}")
except Exception as e:
    ui.show_error(f"Unexpected error: {e}")
```
