#!/bin/bash
# Command-line usage examples for Minifont

echo "=========================================="
echo "Minifont CLI Usage Examples"
echo "=========================================="
echo ""

# Example 1: Basic conversion with local font
echo "1. Convert local TTF font to C header"
echo "   minifont --font myfont.ttf --size 16 --charset ascii --format c-header --output font16.h"
echo ""

# Example 2: Google Fonts
echo "2. Download and convert Google Font"
echo "   minifont --google-font \"Roboto\" --size 16 --charset ascii --format c-header --output roboto16.h"
echo ""

echo "3. Google Font with specific variant"
echo "   minifont --google-font \"Open Sans\" --google-variant bold --size 20 --charset ascii --format xbm"
echo ""

# Example 4: Icon fonts
echo "4. Convert Material Icons (using preset)"
echo "   minifont --icon-font material --icons navigation --size 24 --format c-header"
echo ""

echo "5. Convert specific Font Awesome icons"
echo "   minifont --icon-font fontawesome --icons \"home,user,heart,star\" --size 32 --format c-header"
echo ""

echo "6. Convert Material Icons with custom list"
echo "   minifont --icon-font material --icons \"home,menu,search,settings,favorite\" --size 24 --format xbm"
echo ""

# Example 7: Different formats
echo "7. Export to XBM format (U8g2)"
echo "   minifont --font arial.ttf --size 12 --charset ascii --format xbm --output arial12.xbm"
echo ""

echo "8. Export to BDF format"
echo "   minifont --font ubuntu.ttf --size 16 --charset extended --format bdf --output ubuntu16.bdf"
echo ""

echo "9. Export to Python (MicroPython)"
echo "   minifont --font courier.ttf --size 14 --charset ascii --format python --output font.py"
echo ""

# Example 10: Custom character ranges
echo "10. Convert only digits and uppercase letters"
echo "    minifont --font myfont.ttf --size 16 --charset \"48-57,65-90\" --format c-header"
echo ""

echo "11. Multiple ranges"
echo "    minifont --font myfont.ttf --size 16 --charset \"32-126,160-255\" --format c-header"
echo ""

# Example 12: List options
echo "12. List available presets"
echo "    minifont --list-presets"
echo ""

echo "13. List Google Fonts"
echo "    minifont --list-google-fonts"
echo ""

echo "14. List icon fonts"
echo "    minifont --list-icon-fonts"
echo ""

echo "15. List icon presets"
echo "    minifont --list-icon-presets"
echo ""

# Example 16: With preview
echo "16. Generate with preview"
echo "    minifont --font myfont.ttf --size 16 --charset ascii --format c-header --preview"
echo ""

# Example 17: Interactive mode
echo "17. Interactive mode (no arguments)"
echo "    minifont"
echo ""

echo "=========================================="
echo "For more information, run: minifont --help"
echo "=========================================="
