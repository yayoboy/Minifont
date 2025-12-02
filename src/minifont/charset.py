"""Character set management module."""

from typing import Set, List


class CharsetError(Exception):
    """Exception raised for character set errors."""
    pass


class Charset:
    """Manages character sets for font conversion."""

    # Predefined character set presets
    PRESETS = {
        'ascii': (32, 126),  # Basic ASCII printable characters
        'extended': (32, 255),  # Extended ASCII
        'digits': (48, 57),  # 0-9
        'uppercase': (65, 90),  # A-Z
        'lowercase': (97, 122),  # a-z
    }

    @staticmethod
    def parse_range(range_str: str) -> Set[int]:
        """Parse a character range string into a set of character codes.

        Supported formats:
        - Single range: "32-126"
        - Multiple ranges: "32-90,160-255"
        - Mixed: "32-126,160,170-180"

        Args:
            range_str: Range string to parse

        Returns:
            Set of character codes

        Raises:
            CharsetError: If range string is invalid
        """
        char_codes = set()

        try:
            # Split by comma for multiple ranges
            parts = range_str.split(',')

            for part in parts:
                part = part.strip()

                if '-' in part:
                    # Range like "32-126"
                    start_str, end_str = part.split('-', 1)
                    start = int(start_str.strip())
                    end = int(end_str.strip())

                    if start > end:
                        raise CharsetError(f"Invalid range: start ({start}) > end ({end})")

                    char_codes.update(range(start, end + 1))
                else:
                    # Single character code
                    char_codes.add(int(part))

        except ValueError as e:
            raise CharsetError(f"Invalid character range format: {range_str}. Error: {e}")

        return char_codes

    @staticmethod
    def get_preset(preset_name: str) -> Set[int]:
        """Get a predefined character set.

        Args:
            preset_name: Name of the preset ('ascii', 'extended', etc.)

        Returns:
            Set of character codes

        Raises:
            CharsetError: If preset name is not found
        """
        preset_name = preset_name.lower()

        if preset_name not in Charset.PRESETS:
            available = ', '.join(Charset.PRESETS.keys())
            raise CharsetError(
                f"Unknown preset: '{preset_name}'. Available presets: {available}"
            )

        start, end = Charset.PRESETS[preset_name]
        return set(range(start, end + 1))

    @staticmethod
    def filter_available(char_codes: Set[int], available_chars: Set[int]) -> Set[int]:
        """Filter character codes to only those available in the font.

        Args:
            char_codes: Requested character codes
            available_chars: Character codes available in the font

        Returns:
            Set of character codes that are available
        """
        return char_codes & available_chars

    @staticmethod
    def get_missing(char_codes: Set[int], available_chars: Set[int]) -> Set[int]:
        """Get character codes that are requested but not available in the font.

        Args:
            char_codes: Requested character codes
            available_chars: Character codes available in the font

        Returns:
            Set of missing character codes
        """
        return char_codes - available_chars

    @staticmethod
    def format_charset_info(char_codes: Set[int], max_display: int = 10) -> str:
        """Format character set information for display.

        Args:
            char_codes: Character codes to display
            max_display: Maximum number of characters to show

        Returns:
            Formatted string with character information
        """
        sorted_codes = sorted(char_codes)
        total = len(sorted_codes)

        if total == 0:
            return "No characters"

        # Show first few characters
        display_codes = sorted_codes[:max_display]
        chars_display = [f"{code} ('{chr(code)}')" for code in display_codes if 32 <= code <= 126]

        info = f"Total: {total} characters\n"

        if chars_display:
            info += "Sample: " + ", ".join(chars_display)
            if total > max_display:
                info += f", ... and {total - max_display} more"
        else:
            info += f"Range: {min(sorted_codes)}-{max(sorted_codes)}"

        return info

    @staticmethod
    def get_all_presets() -> List[str]:
        """Get list of all available preset names.

        Returns:
            List of preset names
        """
        return list(Charset.PRESETS.keys())
