# Minifont

A Python CLI tool to convert TTF/OTF/Webfont fonts to 1-bit bitmaps for Arduino and embedded projects.

## Features

- 🔤 Support for TTF, OTF, and WOFF/WOFF2 fonts
- 🌐 **Google Fonts integration** - Download fonts directly from Google Fonts
- 🎯 **Icon fonts support** - Material Icons and Font Awesome with preset collections
- 📊 Multiple export formats:
  - C header arrays (Adafruit GFX compatible)
  - XBM format (U8g2 compatible)
  - BDF bitmap fonts
  - Python byte arrays (MicroPython)
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

### Download and convert Google Fonts
```bash
# Download Roboto from Google Fonts
minifont --google-font "Roboto" --size 16 --charset ascii --format c-header --output roboto16.h

# With specific variant
minifont --google-font "Open Sans" --google-variant bold --size 20 --charset ascii --format xbm
```

### Convert icon fonts
```bash
# Material Icons with preset
minifont --icon-font material --icons navigation --size 24 --format c-header

# Font Awesome with specific icons
minifont --icon-font fontawesome --icons "home,user,heart,star" --size 32 --format c-header

# Material Icons custom selection
minifont --icon-font material --icons "home,menu,search,settings" --size 24 --format xbm
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
- `digits`: Numbers 0-9
- `uppercase`: A-Z
- `lowercase`: a-z
- `custom`: Define your own range (e.g., "32-126,160-180")

## Icon Font Presets

- `navigation`: home, menu, arrows, close
- `actions`: add, remove, edit, delete, save, search
- `media`: play, pause, stop, volume controls
- `communication`: mail, phone, share
- `alerts`: info, warning, error, check
- `common`: frequently used icons

List all available icons:
```bash
minifont --list-icon-presets
```

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
- requests (for Google Fonts)

## Additional Resources

### Google Fonts
- Browse fonts: https://fonts.google.com/
- List popular fonts: `minifont --list-google-fonts`

### Icon Fonts
- Material Icons: https://fonts.google.com/icons
- Font Awesome: https://fontawesome.com/
- List supported: `minifont --list-icon-fonts`

**Note:** Icon font files must be downloaded separately and provided when converting icons.

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
