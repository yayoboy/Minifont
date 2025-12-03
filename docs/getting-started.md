# Getting Started with Minifont

This guide will help you install and start using Minifont quickly.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) FreeType library for font rendering

### Install from PyPI

```bash
pip install minifont
```

### Install from Source

```bash
git clone https://github.com/yayoboy/Minifont.git
cd Minifont
pip install -e .
```

### Verify Installation

```bash
minifont --version
```

Expected output:
```
minifont, version 0.2.0
```

## First Steps

### 1. Interactive Mode (Recommended for Beginners)

Simply run `minifont` without arguments to launch the interactive TUI:

```bash
minifont
```

This will:
- Automatically discover fonts in your current directory
- Show a beautiful terminal UI with file browser
- Allow you to configure parameters interactively
- Preview characters before conversion

### 2. List Available Fonts

Check what fonts are available in your current directory:

```bash
minifont --list-fonts
```

Or in a specific directory:

```bash
minifont --list-fonts --directory /System/Library/Fonts
```

### 3. Simple Batch Conversion

Convert a font file with default settings:

```bash
minifont --font myfont.ttf --size 16 --charset ascii --format c-header --output font.h
```

## Quick Examples

### Convert Local Font

```bash
# Basic conversion
minifont --font Arial.ttf --size 16 --charset ascii --format c-header --output arial16.h

# With preview
minifont --font Arial.ttf --size 16 --charset ascii --format c-header --output arial16.h --preview
```

### Download from Google Fonts

```bash
# List popular Google Fonts
minifont --list-google-fonts

# Download and convert
minifont --google-font "Roboto" --size 16 --charset ascii --format c-header --output roboto16.h
```

### Convert Icon Fonts

```bash
# List supported icon fonts
minifont --list-icon-fonts

# List icon presets
minifont --list-icon-presets

# Use navigation preset
minifont --icon-font material --icons navigation --size 24 --format c-header
```

## Common Use Cases

### For Arduino (Adafruit GFX)

```bash
minifont --font myfont.ttf --size 12 --charset ascii --format c-header --output font12.h
```

Then in your Arduino sketch:
```cpp
#include "font12.h"
display.setFont(&font12);
```

### For U8g2 Library

```bash
minifont --font myfont.ttf --size 16 --charset ascii --format xbm --output font16.xbm
```

### For MicroPython

```bash
minifont --font myfont.ttf --size 8 --charset ascii --format python --output font8.py
```

Then in MicroPython:
```python
from font8 import CustomFont_bitmaps, CustomFont_glyphs
```

## Character Set Options

### Using Presets

```bash
# Basic ASCII (most common)
--charset ascii

# Extended ASCII
--charset extended

# Only digits
--charset digits

# Only uppercase
--charset uppercase

# Only lowercase
--charset lowercase
```

### Custom Ranges

```bash
# Single range
--charset "32-126"

# Multiple ranges
--charset "32-90,160-255"

# Specific characters
--charset "65-90"  # A-Z
```

## Next Steps

- Read the [User Guide](user-guide.md) for detailed usage
- Explore the [API Reference](api-reference.md) for programmatic use
- Check out [Examples](examples.md) for more complex scenarios
- Learn about the [Architecture](architecture.md) to understand how it works

## Getting Help

```bash
# Show all available options
minifont --help

# List character set presets
minifont --list-presets

# List Google Fonts
minifont --list-google-fonts

# List icon fonts
minifont --list-icon-fonts
```

## Troubleshooting

### Font Not Found

If Minifont can't find your font:

1. Make sure the file path is correct
2. Try using `--list-fonts` to see available fonts
3. Use absolute path: `--font /full/path/to/font.ttf`

### No Characters Rendered

If "0 characters" are rasterized:

1. Check that the font contains the requested characters
2. Try a different charset: `--charset ascii`
3. Use a common system font to test

### Permission Denied

On macOS/Linux, you might need to use fonts from accessible directories:

```bash
# Copy font to your working directory
cp /System/Library/Fonts/SomeFont.ttf .
minifont --font SomeFont.ttf ...
```

## Support

- **Issues**: [GitHub Issues](https://github.com/yayoboy/Minifont/issues)
- **Documentation**: This guide and [User Guide](user-guide.md)
- **Examples**: See [Examples](examples.md) directory
