# Minifont

A Python CLI tool to convert TTF/OTF/Webfont fonts to 1-bit bitmaps for Arduino and embedded projects.

## Features

- 🔤 Support for TTF, OTF, and WOFF/WOFF2 fonts
- 📊 Multiple export formats:
  - C header arrays (Adafruit GFX compatible)
  - XBM format (U8g2 compatible)
  - BDF bitmap fonts
  - Python byte arrays (MicroPython)
  - PNG preview
- 🎨 Customizable character sets (ASCII, extended, Unicode ranges)
- 📐 Multiple font sizes (8, 12, 16, 24 px and custom)
- 🖥️ Interactive CLI interface
- ⚡ Batch processing mode

## Installation

```bash
pip install minifont
```

Or install from source:

```bash
git clone https://github.com/yayoboy/Minifont.git
cd Minifont
pip install -e .
```

## Quick Start

Interactive mode:
```bash
minifont
```

Batch mode:
```bash
minifont --font myfont.ttf --size 16 --charset ascii --format c-header --output font_data.h
```

## Usage Examples

### Convert a TTF font to C header
```bash
minifont --font Arial.ttf --size 16 --charset ascii --format c-header --output arial16.h
```

### Generate XBM for U8g2
```bash
minifont --font Roboto.ttf --size 12 --charset "32-126" --format xbm --output roboto12.xbm
```

### Custom character range
```bash
minifont --font myfont.ttf --size 16 --charset "32-90,160-255" --format c-header
```

## Character Set Presets

- `ascii`: Basic ASCII (32-126)
- `extended`: Extended ASCII (32-255)
- `custom`: Define your own range (e.g., "32-126,160-180")

## Export Formats

- **c-header**: C array format for Arduino/embedded (Adafruit GFX compatible)
- **xbm**: X BitMap format (U8g2 library compatible)
- **bdf**: Bitmap Distribution Format
- **python**: Python byte arrays (MicroPython compatible)
- **png**: PNG image preview

## Requirements

- Python 3.8+
- fontTools
- freetype-py
- Pillow
- click

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
