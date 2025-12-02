# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-02

### Added
- **Google Fonts Integration**: Download fonts directly from Google Fonts API
  - `--google-font` option to download fonts by name
  - `--google-variant` option to select font variants (regular, bold, italic, etc.)
  - Automatic font caching to avoid re-downloading
  - `--list-google-fonts` to show popular Google Fonts
- **Icon Fonts Support**: Convert icon fonts to bitmaps
  - Material Icons support with common icon mappings
  - Font Awesome support with common icon mappings
  - `--icon-font` option to specify icon font type
  - `--icons` option to select icons by name or preset
  - Icon presets: navigation, actions, media, communication, alerts, common
  - `--list-icon-fonts` to show supported icon fonts
  - `--list-icon-presets` to show available icon presets
- New modules:
  - `google_fonts.py`: Google Fonts downloader and manager
  - `icon_fonts.py`: Icon font mappings and registry
- Additional character set presets: digits, uppercase, lowercase
- Comprehensive examples for Google Fonts and icon fonts usage
- CLI usage examples script (bash)

### Changed
- Updated CLI to support Google Fonts and icon fonts options
- Enhanced documentation with Google Fonts and icon fonts sections
- Updated version to 0.2.0
- Added `requests` dependency for Google Fonts API

### Dependencies
- Added: requests>=2.31.0

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

[0.2.0]: https://github.com/yayoboy/Minifont/releases/tag/v0.2.0
[0.1.0]: https://github.com/yayoboy/Minifont/releases/tag/v0.1.0
