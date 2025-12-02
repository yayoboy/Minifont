"""Examples for font discovery functionality."""

from minifont import FontDiscovery
from pathlib import Path


def example_find_fonts_current_directory():
    """Example: Find fonts in current directory."""
    print("Example 1: Find fonts in current directory\n")

    # Find all fonts in current directory
    fonts = FontDiscovery.find_fonts_in_directory(".")

    if fonts:
        print(f"Found {len(fonts)} font(s):")
        for i, font in enumerate(fonts, 1):
            print(f"  {i}. {font.filename}")
            print(f"     Name: {font.font_name}")
            print(f"     Format: {font.format}")
            print(f"     Size: {font.size_kb:.1f} KB")
            print(f"     Path: {font.path}")
            print()
    else:
        print("No fonts found in current directory")

    print()


def example_find_fonts_recursive():
    """Example: Find fonts recursively in subdirectories."""
    print("Example 2: Find fonts recursively\n")

    # Find fonts in current directory and subdirectories
    fonts = FontDiscovery.find_fonts_in_directory(".", recursive=True)

    print(f"Found {len(fonts)} font(s) (including subdirectories)")
    print()


def example_find_font_by_name():
    """Example: Find a specific font by name."""
    print("Example 3: Find font by name\n")

    # Search for a font by name
    font_name = "Arial.ttf"
    font_path = FontDiscovery.get_font_by_name(font_name)

    if font_path:
        print(f"Found: {font_name}")
        print(f"Path: {font_path}")
    else:
        print(f"Font not found: {font_name}")

    print()


def example_group_fonts_by_family():
    """Example: Group fonts by family."""
    print("Example 4: Group fonts by family\n")

    # Find all fonts
    fonts = FontDiscovery.find_fonts_in_directory(".")

    if not fonts:
        print("No fonts found")
        return

    # Group by family
    families = FontDiscovery.group_fonts_by_family(fonts)

    print(f"Found {len(families)} font families:")
    for family_name, family_fonts in sorted(families.items()):
        print(f"\n  📁 {family_name}")
        for font in family_fonts:
            print(f"     • {font.filename} ({font.format})")

    print()


def example_format_font_list():
    """Example: Format font list for display."""
    print("Example 5: Format font list\n")

    # Find fonts
    fonts = FontDiscovery.find_fonts_in_directory(".")

    # Format for display
    formatted = FontDiscovery.format_font_list(fonts, max_display=5)
    print(formatted)

    print()


def example_search_in_specific_directory():
    """Example: Search fonts in a specific directory."""
    print("Example 6: Search in specific directory\n")

    # Search in a specific directory
    directory = "/usr/share/fonts"  # Common font directory on Linux
    # On macOS: "/Library/Fonts" or "~/Library/Fonts"
    # On Windows: "C:\\Windows\\Fonts"

    try:
        fonts = FontDiscovery.find_fonts_in_directory(directory, recursive=True)
        print(f"Found {len(fonts)} fonts in {directory}")

        # Show first 5
        for font in fonts[:5]:
            print(f"  • {font.filename} - {font.font_name}")

        if len(fonts) > 5:
            print(f"  ... and {len(fonts) - 5} more")

    except Exception as e:
        print(f"Error: {e}")

    print()


def example_cli_integration():
    """Example: How font discovery integrates with CLI."""
    print("Example 7: CLI Integration\n")

    print("Font discovery is automatically used in the CLI:\n")

    print("1. List fonts in current directory:")
    print("   $ minifont --list-fonts\n")

    print("2. List fonts in specific directory:")
    print("   $ minifont --list-fonts --directory /path/to/fonts\n")

    print("3. Interactive mode automatically discovers fonts:")
    print("   $ minifont")
    print("   (will show fonts found in current directory)\n")

    print("4. Use discovered font by name:")
    print("   $ minifont --font Arial.ttf --size 16 --charset ascii --format c-header\n")

    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Font Discovery Examples for Minifont")
    print("=" * 60)
    print()

    example_find_fonts_current_directory()
    example_find_fonts_recursive()
    example_find_font_by_name()
    example_group_fonts_by_family()
    example_format_font_list()
    example_search_in_specific_directory()
    example_cli_integration()

    print("=" * 60)
    print("\nTip: Copy some font files to the current directory")
    print("to see more detailed examples!")
