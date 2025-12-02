"""Font loading and validation module."""

import os
from pathlib import Path
from typing import Optional
from fontTools.ttLib import TTFont


class FontLoaderError(Exception):
    """Exception raised for font loading errors."""
    pass


class FontLoader:
    """Handles loading and validation of font files."""

    SUPPORTED_EXTENSIONS = {'.ttf', '.otf', '.woff', '.woff2'}

    def __init__(self, font_path: str):
        """Initialize the font loader.

        Args:
            font_path: Path to the font file

        Raises:
            FontLoaderError: If font file is invalid or unsupported
        """
        self.font_path = Path(font_path)
        self.font: Optional[TTFont] = None

        self._validate_path()
        self._load_font()

    def _validate_path(self) -> None:
        """Validate that the font file exists and is supported."""
        if not self.font_path.exists():
            raise FontLoaderError(f"Font file not found: {self.font_path}")

        if not self.font_path.is_file():
            raise FontLoaderError(f"Path is not a file: {self.font_path}")

        if self.font_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise FontLoaderError(
                f"Unsupported font format: {self.font_path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

    def _load_font(self) -> None:
        """Load the font file using fontTools."""
        try:
            self.font = TTFont(str(self.font_path))
        except Exception as e:
            raise FontLoaderError(f"Failed to load font: {e}")

    def validate(self) -> bool:
        """Validate the loaded font.

        Returns:
            True if font is valid

        Raises:
            FontLoaderError: If font is invalid
        """
        if self.font is None:
            raise FontLoaderError("No font loaded")

        # Check for required tables
        required_tables = {'cmap', 'glyf', 'head', 'hhea', 'hmtx', 'maxp', 'name', 'post'}
        missing_tables = required_tables - set(self.font.keys())

        if missing_tables:
            raise FontLoaderError(f"Font is missing required tables: {', '.join(missing_tables)}")

        return True

    def get_font_name(self) -> str:
        """Get the font family name.

        Returns:
            Font family name
        """
        if self.font is None:
            return "Unknown"

        name_table = self.font['name']
        # Try to get the font family name (nameID 1)
        for record in name_table.names:
            if record.nameID == 1:
                return record.toUnicode()

        return self.font_path.stem

    def get_available_characters(self) -> set[int]:
        """Get set of available character codes in the font.

        Returns:
            Set of character codes (Unicode code points)
        """
        if self.font is None:
            return set()

        cmap = self.font.getBestCmap()
        if cmap is None:
            return set()

        return set(cmap.keys())

    def has_character(self, char_code: int) -> bool:
        """Check if font contains a specific character.

        Args:
            char_code: Unicode code point

        Returns:
            True if character is available
        """
        return char_code in self.get_available_characters()

    def get_font(self) -> TTFont:
        """Get the loaded TTFont object.

        Returns:
            TTFont object

        Raises:
            FontLoaderError: If no font is loaded
        """
        if self.font is None:
            raise FontLoaderError("No font loaded")
        return self.font
