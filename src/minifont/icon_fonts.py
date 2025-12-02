"""Icon fonts support module."""

from typing import Dict, Set, List, Tuple
from dataclasses import dataclass


@dataclass
class IconMapping:
    """Mapping between icon name and Unicode code point."""
    name: str
    code: int
    aliases: List[str] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class IconFontError(Exception):
    """Exception raised for icon font errors."""
    pass


class IconFont:
    """Base class for icon font support."""

    def __init__(self):
        """Initialize icon font."""
        self.icons: Dict[str, IconMapping] = {}
        self._load_mappings()

    def _load_mappings(self):
        """Load icon mappings. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _load_mappings()")

    def get_icon_code(self, icon_name: str) -> int:
        """Get Unicode code point for an icon name.

        Args:
            icon_name: Icon name or alias

        Returns:
            Unicode code point

        Raises:
            IconFontError: If icon not found
        """
        icon_name_lower = icon_name.lower().replace("-", "_")

        # Direct match
        if icon_name_lower in self.icons:
            return self.icons[icon_name_lower].code

        # Check aliases
        for icon in self.icons.values():
            if icon_name_lower in [a.lower() for a in icon.aliases]:
                return icon.code

        raise IconFontError(f"Icon not found: {icon_name}")

    def list_icons(self) -> List[str]:
        """Get list of all available icon names.

        Returns:
            List of icon names
        """
        return sorted(self.icons.keys())

    def search_icons(self, query: str) -> List[str]:
        """Search for icons by name.

        Args:
            query: Search query

        Returns:
            List of matching icon names
        """
        query_lower = query.lower()
        matches = []

        for name in self.icons.keys():
            if query_lower in name.lower():
                matches.append(name)

        return sorted(matches)

    def get_all_codes(self) -> Set[int]:
        """Get set of all icon code points.

        Returns:
            Set of Unicode code points
        """
        return {icon.code for icon in self.icons.values()}


class MaterialIcons(IconFont):
    """Material Design Icons support."""

    def _load_mappings(self):
        """Load Material Icons mappings."""
        # Common Material Icons (subset)
        # Full list: https://fonts.google.com/icons
        material_icons = {
            "home": 0xE88A,
            "menu": 0xE5D2,
            "settings": 0xE8B8,
            "search": 0xE8B6,
            "favorite": 0xE87D,
            "star": 0xE838,
            "delete": 0xE872,
            "add": 0xE145,
            "remove": 0xE15B,
            "close": 0xE5CD,
            "check": 0xE5CA,
            "arrow_back": 0xE5C4,
            "arrow_forward": 0xE5C8,
            "arrow_up": 0xE5D8,
            "arrow_down": 0xE5DB,
            "info": 0xE88E,
            "warning": 0xE002,
            "error": 0xE000,
            "help": 0xE887,
            "account": 0xE853,
            "lock": 0xE897,
            "mail": 0xE158,
            "phone": 0xE0CD,
            "calendar": 0xE878,
            "camera": 0xE3AF,
            "edit": 0xE3C9,
            "save": 0xE161,
            "print": 0xE8AD,
            "share": 0xE80D,
            "cloud": 0xE2BD,
            "download": 0xE2C4,
            "upload": 0xE2C6,
            "refresh": 0xE5D5,
            "play": 0xE037,
            "pause": 0xE034,
            "stop": 0xE047,
            "volume_up": 0xE050,
            "volume_down": 0xE04D,
            "brightness": 0xE1C6,
            "wifi": 0xE63E,
            "bluetooth": 0xE1A7,
            "battery": 0xE1A3,
        }

        for name, code in material_icons.items():
            self.icons[name] = IconMapping(name=name, code=code)


class FontAwesome(IconFont):
    """Font Awesome icons support."""

    def _load_mappings(self):
        """Load Font Awesome mappings."""
        # Common Font Awesome icons (subset)
        # Full list: https://fontawesome.com/icons
        fa_icons = {
            "home": 0xF015,
            "user": 0xF007,
            "search": 0xF002,
            "heart": 0xF004,
            "star": 0xF005,
            "cog": 0xF013,
            "trash": 0xF1F8,
            "edit": 0xF044,
            "plus": 0xF067,
            "minus": 0xF068,
            "times": 0xF00D,
            "check": 0xF00C,
            "arrow_left": 0xF060,
            "arrow_right": 0xF061,
            "arrow_up": 0xF062,
            "arrow_down": 0xF063,
            "info_circle": 0xF05A,
            "warning": 0xF071,
            "bell": 0xF0F3,
            "calendar": 0xF073,
            "camera": 0xF030,
            "envelope": 0xF0E0,
            "phone": 0xF095,
            "lock": 0xF023,
            "unlock": 0xF09C,
            "download": 0xF019,
            "upload": 0xF093,
            "cloud": 0xF0C2,
            "play": 0xF04B,
            "pause": 0xF04C,
            "stop": 0xF04D,
            "wifi": 0xF1EB,
            "battery_full": 0xF240,
            "battery_half": 0xF242,
            "battery_empty": 0xF244,
        }

        for name, code in fa_icons.items():
            self.icons[name] = IconMapping(name=name, code=code)


class IconFontRegistry:
    """Registry of supported icon fonts."""

    _ICON_FONTS = {
        "material": MaterialIcons,
        "fontawesome": FontAwesome,
        "fa": FontAwesome,  # Alias
    }

    @classmethod
    def get_icon_font(cls, name: str) -> IconFont:
        """Get an icon font by name.

        Args:
            name: Icon font name (material, fontawesome, fa)

        Returns:
            IconFont instance

        Raises:
            IconFontError: If icon font not found
        """
        name_lower = name.lower()

        if name_lower not in cls._ICON_FONTS:
            available = ", ".join(cls._ICON_FONTS.keys())
            raise IconFontError(
                f"Unknown icon font: {name}. Available: {available}"
            )

        return cls._ICON_FONTS[name_lower]()

    @classmethod
    def list_icon_fonts(cls) -> List[str]:
        """Get list of supported icon fonts.

        Returns:
            List of icon font names
        """
        return list(cls._ICON_FONTS.keys())

    @classmethod
    def get_icon_codes(cls, icon_font_name: str, icon_names: List[str]) -> Set[int]:
        """Get Unicode code points for multiple icons.

        Args:
            icon_font_name: Icon font name
            icon_names: List of icon names

        Returns:
            Set of Unicode code points

        Raises:
            IconFontError: If icon font or icon not found
        """
        icon_font = cls.get_icon_font(icon_font_name)
        codes = set()

        for icon_name in icon_names:
            try:
                codes.add(icon_font.get_icon_code(icon_name))
            except IconFontError as e:
                # Log warning but continue
                print(f"Warning: {e}")

        return codes


# Preset icon collections
ICON_PRESETS = {
    "navigation": ["home", "menu", "arrow_back", "arrow_forward", "close"],
    "actions": ["add", "remove", "edit", "delete", "save", "search"],
    "media": ["play", "pause", "stop", "volume_up", "volume_down"],
    "communication": ["mail", "phone", "share"],
    "alerts": ["info", "warning", "error", "check"],
    "common": ["home", "search", "settings", "favorite", "star", "info", "help"],
}


def get_icon_preset(preset_name: str, icon_font_name: str = "material") -> Set[int]:
    """Get icon codes from a preset collection.

    Args:
        preset_name: Preset name (navigation, actions, media, etc.)
        icon_font_name: Icon font to use

    Returns:
        Set of Unicode code points

    Raises:
        IconFontError: If preset not found
    """
    if preset_name not in ICON_PRESETS:
        available = ", ".join(ICON_PRESETS.keys())
        raise IconFontError(
            f"Unknown icon preset: {preset_name}. Available: {available}"
        )

    icon_names = ICON_PRESETS[preset_name]
    return IconFontRegistry.get_icon_codes(icon_font_name, icon_names)
