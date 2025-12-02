"""Examples for using Google Fonts with Minifont."""

from minifont import GoogleFontsDownloader, FontLoader, FontRasterizer, CHeaderExporter
from minifont.charset import Charset


def example_download_google_font():
    """Example: Download and convert a Google Font."""
    print("Example 1: Download Google Font and convert\n")

    # Initialize downloader
    downloader = GoogleFontsDownloader()

    # Download Roboto font
    font_path = downloader.download_font("Roboto", variant="regular")
    print(f"Downloaded: {font_path}")

    # Load and convert
    loader = FontLoader(font_path)
    char_codes = Charset.get_preset('ascii')
    available = loader.get_available_characters()
    char_codes = Charset.filter_available(char_codes, available)

    rasterizer = FontRasterizer(font_path, size=16)
    glyphs = rasterizer.rasterize_charset(char_codes)

    # Export
    exporter = CHeaderExporter("Roboto")
    exporter.export(glyphs, "output/roboto16.h")

    print("✓ Converted Roboto to C header\n")


def example_download_multiple_variants():
    """Example: Download multiple font variants."""
    print("Example 2: Download multiple variants\n")

    downloader = GoogleFontsDownloader()

    variants = ["regular", "bold", "italic"]
    font_name = "Open Sans"

    for variant in variants:
        print(f"Downloading {font_name} {variant}...")
        font_path = downloader.download_font(font_name, variant=variant)
        print(f"  Saved to: {font_path}")

    print("\n✓ Downloaded all variants\n")


def example_cache_management():
    """Example: Manage font cache."""
    print("Example 3: Font cache management\n")

    downloader = GoogleFontsDownloader()

    # Download a font (will be cached)
    print("First download (from web)...")
    font_path = downloader.download_font("Lato", variant="regular")
    print(f"Downloaded: {font_path}")

    # Download again (will use cache)
    print("\nSecond download (from cache)...")
    font_path = downloader.download_font("Lato", variant="regular")
    print(f"From cache: {font_path}")

    # Force re-download
    print("\nForced re-download...")
    font_path = downloader.download_font("Lato", variant="regular", force=True)
    print(f"Re-downloaded: {font_path}")

    # Clear cache
    print("\nClearing cache...")
    count = downloader.clear_cache()
    print(f"✓ Cleared {count} cached fonts\n")


def example_popular_fonts():
    """Example: Download popular Google Fonts."""
    print("Example 4: Popular Google Fonts\n")

    from minifont.google_fonts import POPULAR_GOOGLE_FONTS

    downloader = GoogleFontsDownloader()

    print("Popular Google Fonts:")
    for font_name in POPULAR_GOOGLE_FONTS[:5]:  # First 5
        print(f"  • {font_name}")
        font_path = downloader.download_font(font_name, variant="regular")
        print(f"    → {font_path}")

    print("\n✓ Downloaded popular fonts\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Google Fonts Examples for Minifont")
    print("=" * 60)
    print()

    print("Uncomment examples to run them:\n")

    # Uncomment to run:
    # example_download_google_font()
    # example_download_multiple_variants()
    # example_cache_management()
    # example_popular_fonts()

    print("Note: These examples require internet connection")
    print("to download fonts from Google Fonts.")
