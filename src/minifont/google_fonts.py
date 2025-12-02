"""Google Fonts downloader and manager."""

import os
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urljoin


class GoogleFontsError(Exception):
    """Exception raised for Google Fonts errors."""
    pass


class GoogleFontsDownloader:
    """Downloads fonts from Google Fonts API."""

    # Google Fonts API endpoint
    API_BASE_URL = "https://www.googleapis.com/webfonts/v1/webfonts"

    # Google Fonts CDN
    FONTS_CDN_BASE = "https://fonts.googleapis.com/css"

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """Initialize Google Fonts downloader.

        Args:
            api_key: Google Fonts API key (optional, for listing fonts)
            cache_dir: Directory to cache downloaded fonts
        """
        self.api_key = api_key
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".minifont" / "fonts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def list_fonts(self, sort: str = "popularity") -> List[Dict]:
        """List available fonts from Google Fonts.

        Args:
            sort: Sort order (popularity, alpha, date, trending)

        Returns:
            List of font metadata dictionaries

        Raises:
            GoogleFontsError: If API request fails
        """
        if not self.api_key:
            raise GoogleFontsError(
                "API key required to list fonts. "
                "Get one at https://developers.google.com/fonts/docs/developer_api"
            )

        try:
            params = {
                "key": self.api_key,
                "sort": sort
            }
            response = requests.get(self.API_BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get("items", [])

        except requests.RequestException as e:
            raise GoogleFontsError(f"Failed to fetch fonts list: {e}")

    def search_font(self, font_name: str) -> Optional[Dict]:
        """Search for a specific font by name.

        Args:
            font_name: Font family name to search for

        Returns:
            Font metadata dictionary or None if not found
        """
        try:
            fonts = self.list_fonts()
            font_name_lower = font_name.lower()

            for font in fonts:
                if font.get("family", "").lower() == font_name_lower:
                    return font

            return None

        except GoogleFontsError:
            return None

    def download_font(
        self,
        font_family: str,
        variant: str = "regular",
        force: bool = False
    ) -> str:
        """Download a font from Google Fonts.

        Args:
            font_family: Font family name (e.g., "Roboto", "Open Sans")
            variant: Font variant (regular, bold, italic, etc.)
            force: Force re-download even if cached

        Returns:
            Path to downloaded font file

        Raises:
            GoogleFontsError: If download fails
        """
        # Sanitize font name for filename
        safe_name = font_family.replace(" ", "_")
        cache_file = self.cache_dir / f"{safe_name}_{variant}.ttf"

        # Check cache
        if cache_file.exists() and not force:
            return str(cache_file)

        try:
            # Request font CSS
            params = {
                "family": f"{font_family}:{variant}"
            }
            response = requests.get(self.FONTS_CDN_BASE, params=params, timeout=10)
            response.raise_for_status()

            # Parse CSS to find TTF URL
            css_content = response.text
            font_url = self._extract_font_url_from_css(css_content)

            if not font_url:
                raise GoogleFontsError(f"Could not find font URL for {font_family}:{variant}")

            # Download the actual font file
            font_response = requests.get(font_url, timeout=30)
            font_response.raise_for_status()

            # Save to cache
            cache_file.write_bytes(font_response.content)

            return str(cache_file)

        except requests.RequestException as e:
            raise GoogleFontsError(f"Failed to download font: {e}")

    def _extract_font_url_from_css(self, css: str) -> Optional[str]:
        """Extract font URL from CSS content.

        Args:
            css: CSS content from Google Fonts

        Returns:
            Font file URL or None
        """
        # Look for url() in CSS
        import re

        # Match TTF, OTF, or WOFF2 URLs
        pattern = r'url\((https?://[^\)]+\.(?:ttf|otf|woff2))\)'
        match = re.search(pattern, css)

        if match:
            return match.group(1)

        return None

    def get_font_variants(self, font_family: str) -> List[str]:
        """Get available variants for a font.

        Args:
            font_family: Font family name

        Returns:
            List of available variants

        Raises:
            GoogleFontsError: If font not found
        """
        font_info = self.search_font(font_family)

        if not font_info:
            raise GoogleFontsError(f"Font not found: {font_family}")

        return font_info.get("variants", [])

    def clear_cache(self) -> int:
        """Clear downloaded fonts cache.

        Returns:
            Number of files deleted
        """
        count = 0
        for font_file in self.cache_dir.glob("*.ttf"):
            font_file.unlink()
            count += 1

        return count


# Popular Google Fonts presets
POPULAR_GOOGLE_FONTS = [
    "Roboto",
    "Open Sans",
    "Lato",
    "Montserrat",
    "Oswald",
    "Source Sans Pro",
    "Raleway",
    "PT Sans",
    "Merriweather",
    "Ubuntu",
]
