# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-02

### Added
- Initial release of Minifont
- Font loading support for TTF, OTF, WOFF, WOFF2 formats
- Character set presets (ASCII, extended, custom ranges)
- 1-bit monochrome bitmap rasterization using FreeType
- Multiple export formats:
  - C header arrays (Adafruit GFX compatible)
  - XBM format (U8g2 compatible)
  - BDF (Bitmap Distribution Format)
  - Python byte arrays (MicroPython)
- Interactive CLI interface with Click
- Batch processing mode with command-line flags
- Text preview of generated bitmaps
- Comprehensive unit tests
- Usage examples for Python and Arduino
- Complete documentation (README, CONTRIBUTING, LICENSE)

### Features
- Customizable font sizes (8, 12, 16, 24 px and custom)
- Character validation and filtering
- Font metrics extraction
- Support for fixed and proportional width fonts

[0.1.0]: https://github.com/yayoboy/Minifont/releases/tag/v0.1.0
