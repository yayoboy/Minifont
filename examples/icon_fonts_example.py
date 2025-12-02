"""Examples for using icon fonts with Minifont."""

from minifont import FontRasterizer, CHeaderExporter
from minifont.icon_fonts import (
    MaterialIcons,
    FontAwesome,
    IconFontRegistry,
    get_icon_preset,
    ICON_PRESETS
)


def example_material_icons():
    """Example: Convert Material Design Icons."""
    print("Example 1: Material Design Icons\n")

    # Get Material Icons font
    material = MaterialIcons()

    # Get specific icon codes
    icons = {
        "home": material.get_icon_code("home"),
        "search": material.get_icon_code("search"),
        "settings": material.get_icon_code("settings"),
    }

    print("Material Icons codes:")
    for name, code in icons.items():
        print(f"  • {name}: U+{code:04X}")

    # Collect all codes
    char_codes = set(icons.values())

    # Note: You need to download Material Icons font separately
    # from https://fonts.google.com/icons
    font_path = "path/to/MaterialIcons-Regular.ttf"

    # Rasterize
    # rasterizer = FontRasterizer(font_path, size=24)
    # glyphs = rasterizer.rasterize_charset(char_codes)
    #
    # # Export
    # exporter = CHeaderExporter("MaterialIcons")
    # exporter.export(glyphs, "output/material_icons24.h")

    print("\n✓ Material Icons example (update font_path to run)\n")


def example_font_awesome():
    """Example: Convert Font Awesome icons."""
    print("Example 2: Font Awesome Icons\n")

    # Get Font Awesome font
    fa = FontAwesome()

    # Get specific icon codes
    icons = {
        "home": fa.get_icon_code("home"),
        "user": fa.get_icon_code("user"),
        "heart": fa.get_icon_code("heart"),
    }

    print("Font Awesome icon codes:")
    for name, code in icons.items():
        print(f"  • {name}: U+{code:04X}")

    print("\n✓ Font Awesome example\n")


def example_icon_presets():
    """Example: Use icon presets."""
    print("Example 3: Icon Presets\n")

    # List available presets
    print("Available icon presets:")
    for preset_name, icon_list in ICON_PRESETS.items():
        print(f"  • {preset_name}: {', '.join(icon_list[:3])}...")

    # Get codes from preset
    print("\nUsing 'navigation' preset:")
    nav_codes = get_icon_preset("navigation", "material")
    print(f"  {len(nav_codes)} icons selected")

    # Get codes from preset
    print("\nUsing 'actions' preset:")
    action_codes = get_icon_preset("actions", "material")
    print(f"  {len(action_codes)} icons selected")

    print("\n✓ Icon presets example\n")


def example_search_icons():
    """Example: Search for icons."""
    print("Example 4: Search Icons\n")

    material = MaterialIcons()

    # Search for icons
    query = "arrow"
    results = material.search_icons(query)

    print(f"Icons matching '{query}':")
    for icon_name in results:
        code = material.get_icon_code(icon_name)
        print(f"  • {icon_name}: U+{code:04X}")

    print("\n✓ Icon search example\n")


def example_list_all_icons():
    """Example: List all available icons."""
    print("Example 5: List All Icons\n")

    material = MaterialIcons()

    all_icons = material.list_icons()
    print(f"Total Material Icons available: {len(all_icons)}")
    print("\nFirst 10 icons:")
    for icon_name in all_icons[:10]:
        code = material.get_icon_code(icon_name)
        print(f"  • {icon_name}: U+{code:04X}")

    print("\n✓ List all icons example\n")


def example_registry():
    """Example: Use IconFontRegistry."""
    print("Example 6: Icon Font Registry\n")

    # List supported icon fonts
    print("Supported icon fonts:")
    for font_name in IconFontRegistry.list_icon_fonts():
        print(f"  • {font_name}")

    # Get icon font by name
    material = IconFontRegistry.get_icon_font("material")
    print(f"\nLoaded: {type(material).__name__}")

    # Get multiple icon codes at once
    icon_names = ["home", "menu", "search", "settings"]
    codes = IconFontRegistry.get_icon_codes("material", icon_names)
    print(f"\nGot {len(codes)} icon codes")

    print("\n✓ Registry example\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Icon Fonts Examples for Minifont")
    print("=" * 60)
    print()

    example_material_icons()
    example_font_awesome()
    example_icon_presets()
    example_search_icons()
    example_list_all_icons()
    example_registry()

    print("=" * 60)
    print("\nTo use icon fonts, download the font files:")
    print("  • Material Icons: https://fonts.google.com/icons")
    print("  • Font Awesome: https://fontawesome.com/")
