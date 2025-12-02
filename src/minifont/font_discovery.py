"""Font discovery utilities for finding fonts in directories."""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from .font_loader import FontLoader


@dataclass
class FontInfo:
    """Information about a discovered font file."""
    path: Path
    filename: str
    size_kb: float
    font_name: Optional[str] = None
    format: Optional[str] = None

    def __str__(self) -> str:
        """String representation of font info."""
        name = self.font_name or "Unknown"
        return f"{self.filename} ({self.format}, {self.size_kb:.1f} KB) - {name}"


class FontDiscovery:
    """Discovers and lists font files in directories."""

    # Supported font extensions
    FONT_EXTENSIONS = {'.ttf', '.otf', '.woff', '.woff2'}

    @staticmethod
    def find_fonts_in_directory(directory: str = ".", recursive: bool = False) -> List[FontInfo]:
        """Find all font files in a directory.

        Args:
            directory: Directory to search (default: current directory)
            recursive: If True, search subdirectories recursively

        Returns:
            List of FontInfo objects for discovered fonts
        """
        directory_path = Path(directory).resolve()
        fonts = []

        if not directory_path.exists() or not directory_path.is_dir():
            return fonts

        # Search pattern
        if recursive:
            patterns = [f"**/*{ext}" for ext in FontDiscovery.FONT_EXTENSIONS]
        else:
            patterns = [f"*{ext}" for ext in FontDiscovery.FONT_EXTENSIONS]

        # Find all font files
        font_files = []
        for pattern in patterns:
            font_files.extend(directory_path.glob(pattern))

        # Get info for each font
        for font_file in sorted(font_files):
            try:
                font_info = FontDiscovery._get_font_info(font_file)
                if font_info:
                    fonts.append(font_info)
            except Exception:
                # Skip files that can't be read
                continue

        return fonts

    @staticmethod
    def _get_font_info(font_path: Path) -> Optional[FontInfo]:
        """Get information about a font file.

        Args:
            font_path: Path to font file

        Returns:
            FontInfo object or None if file can't be read
        """
        try:
            # Get file size
            size_bytes = font_path.stat().st_size
            size_kb = size_bytes / 1024

            # Get font format from extension
            font_format = font_path.suffix.upper().replace('.', '')

            # Try to get font name
            font_name = None
            try:
                loader = FontLoader(str(font_path))
                font_name = loader.get_font_name()
            except Exception:
                # If we can't load the font, just use filename
                font_name = font_path.stem

            return FontInfo(
                path=font_path,
                filename=font_path.name,
                size_kb=size_kb,
                font_name=font_name,
                format=font_format
            )

        except Exception:
            return None

    @staticmethod
    def get_font_by_name(name: str, directory: str = ".") -> Optional[Path]:
        """Find a font by name in directory.

        Args:
            name: Font filename (with or without extension)
            directory: Directory to search

        Returns:
            Path to font file or None if not found
        """
        fonts = FontDiscovery.find_fonts_in_directory(directory)

        # Try exact match with filename
        for font in fonts:
            if font.filename.lower() == name.lower():
                return font.path

        # Try match without extension
        name_without_ext = Path(name).stem.lower()
        for font in fonts:
            if font.path.stem.lower() == name_without_ext:
                return font.path

        return None

    @staticmethod
    def format_font_list(fonts: List[FontInfo], max_display: int = 20) -> str:
        """Format list of fonts for display.

        Args:
            fonts: List of FontInfo objects
            max_display: Maximum number of fonts to display

        Returns:
            Formatted string
        """
        if not fonts:
            return "No fonts found in current directory."

        lines = [f"Found {len(fonts)} font(s):\n"]

        for i, font in enumerate(fonts[:max_display], 1):
            lines.append(f"  {i}. {font}")

        if len(fonts) > max_display:
            lines.append(f"\n  ... and {len(fonts) - max_display} more")

        return '\n'.join(lines)

    @staticmethod
    def group_fonts_by_family(fonts: List[FontInfo]) -> Dict[str, List[FontInfo]]:
        """Group fonts by family name.

        Args:
            fonts: List of FontInfo objects

        Returns:
            Dictionary mapping family names to font lists
        """
        families = {}

        for font in fonts:
            # Extract family name (before variant like "Bold", "Italic", etc.)
            family_name = font.font_name or font.path.stem

            # Try to extract base family name
            for variant in ['Bold', 'Italic', 'Regular', 'Light', 'Medium', 'Black']:
                if variant in family_name:
                    family_name = family_name.replace(variant, '').strip()
                    break

            if family_name not in families:
                families[family_name] = []

            families[family_name].append(font)

        return families
